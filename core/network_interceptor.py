"""
网络请求拦截器
拦截淘宝商品详情API响应，提取结构化数据
"""
import asyncio
import json
import re
from typing import Callable, Optional
from playwright.async_api import Page, Response


class NetworkInterceptor:
    """拦截淘宝API响应，获取商品数据"""

    def __init__(self):
        self._intercepted_data: dict = {}
        self._detail_data: Optional[dict] = None
        self._desc_data: Optional[dict] = None
        self._lock = asyncio.Lock()
        self._detail_event = asyncio.Event()
        self._desc_event = asyncio.Event()

    async def start(self, page: Page):
        """开始监听网络请求"""
        page.on("response", self._on_response)

    async def _on_response(self, response: Response):
        """处理网络响应"""
        url = response.url

        # 拦截商品详情API
        if "mtop.taobao.detail.getdetail" in url:
            try:
                body = await response.text()
                # 淘宝API返回的是 JSONP 格式: mtopjsonp(...)
                json_str = self._extract_json_from_jsonp(body)
                if json_str:
                    data = json.loads(json_str)
                    async with self._lock:
                        self._detail_data = data
                    self._detail_event.set()
            except Exception:
                pass

        # 拦截商品描述API
        elif "mtop.taobao.detail.getdesc" in url:
            try:
                body = await response.text()
                json_str = self._extract_json_from_jsonp(body)
                if json_str:
                    data = json.loads(json_str)
                    async with self._lock:
                        self._desc_data = data
                    self._desc_event.set()
            except Exception:
                pass

    def _extract_json_from_jsonp(self, body: str) -> Optional[str]:
        """从JSONP响应中提取JSON"""
        # 匹配 mtopjsonp(...) 或 mtopjsonp123(...)
        match = re.search(r'mtopjsonp\d*\((.*)\)', body, re.DOTALL)
        if match:
            return match.group(1)
        # 尝试直接解析JSON
        try:
            json.loads(body)
            return body
        except (json.JSONDecodeError, ValueError):
            return None

    async def wait_for_detail(self, timeout: float = 15.0) -> Optional[dict]:
        """等待商品详情API响应"""
        try:
            await asyncio.wait_for(self._detail_event.wait(), timeout=timeout)
            async with self._lock:
                return self._detail_data
        except asyncio.TimeoutError:
            return None

    async def wait_for_desc(self, timeout: float = 10.0) -> Optional[dict]:
        """等待商品描述API响应"""
        try:
            await asyncio.wait_for(self._desc_event.wait(), timeout=timeout)
            async with self._lock:
                return self._desc_data
        except asyncio.TimeoutError:
            return None

    async def parse_detail_response(self, data: dict) -> dict:
        """解析商品详情API响应"""
        result = {}
        try:
            api_data = data.get("data", {})

            # 基本信息
            item = api_data.get("item", {})
            result["title"] = item.get("title", "")
            result["item_id"] = item.get("itemId", "")

            # 图片
            images = item.get("images", [])
            if images:
                result["images"] = [
                    url if url.startswith("http") else "https:" + url
                    for url in images
                ]

            # 价格
            price_data = api_data.get("price", {})
            price_info = price_data.get("price", {})
            if price_info:
                try:
                    result["price"] = float(price_info.get("priceText", "0"))
                except (ValueError, TypeError):
                    result["price"] = 0.0
            # 备用价格字段
            if not result.get("price"):
                price_extra = api_data.get("price", {}).get("extraPrice", {})
                if price_extra:
                    try:
                        result["price"] = float(price_extra.get("priceText", "0"))
                    except (ValueError, TypeError):
                        pass

            # SKU
            sku_base = api_data.get("skuBase", {})
            sku_core = api_data.get("skuCore", {})
            if sku_base:
                result["sku_list"] = self._parse_sku(sku_base, sku_core)

            # 商品属性
            props_list = api_data.get("propsList", [])
            if props_list:
                result["attributes"] = self._parse_attributes(props_list)

            # 店铺信息
            seller = api_data.get("seller", {})
            result["shop_name"] = seller.get("shopTitle", "")

            # 销量
            item_data = api_data.get("apiStack", [])
            if item_data:
                try:
                    api_info = json.loads(item_data[0].get("value", "{}"))
                    result["sales_count"] = api_info.get("quantity", {}).get("sellCount", "")
                except (json.JSONDecodeError, IndexError, TypeError):
                    pass

        except Exception:
            pass
        return result

    def _parse_sku(self, sku_base: dict, sku_core: dict) -> list:
        """解析SKU数据"""
        sku_list = []
        try:
            props = sku_base.get("props", [])
            skus = sku_base.get("skus", [])
            price_map = {}

            # 从skuCore获取价格映射
            if sku_core:
                sku_prices = sku_core.get("sku2info", {})
                for sku_id, info in sku_prices.items():
                    price_map[sku_id] = float(info.get("price", {}).get("price", 0))

            for sku in skus:
                sku_id = sku.get("skuId", "")
                prop_path = sku.get("propPath", "")

                # 解析propPath获取规格名称
                name_parts = []
                for prop in props:
                    pid = prop.get("pid", "")
                    values = prop.get("values", [])
                    for val in values:
                        vid = val.get("vid", "")
                        if f"{pid}:{vid}" in prop_path:
                            name_parts.append(val.get("name", ""))

                sku_item = {
                    "name": "/".join(name_parts) if name_parts else f"SKU-{sku_id}",
                    "price": price_map.get(sku_id, 0.0),
                    "stock": sku.get("stock", 100),
                    "sku_code": sku_id,
                    "prop_path": prop_path,
                }
                sku_list.append(sku_item)
        except Exception:
            pass
        return sku_list

    def _parse_attributes(self, props_list) -> dict:
        """解析商品属性"""
        attrs = {}
        try:
            if isinstance(props_list, list):
                for prop in props_list:
                    name = prop.get("name", "")
                    value = prop.get("value", "")
                    if name:
                        attrs[name] = value
            elif isinstance(props_list, dict):
                for key, value in props_list.items():
                    attrs[str(key)] = str(value)
        except Exception:
            pass
        return attrs

    def reset(self):
        """重置拦截器状态"""
        self._detail_data = None
        self._desc_data = None
        self._detail_event.clear()
        self._desc_event.clear()
