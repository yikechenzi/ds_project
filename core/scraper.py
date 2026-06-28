"""
商品采集器
组合使用网络拦截和DOM解析两种方式采集商品信息
"""
import asyncio
import re
from typing import Optional
from playwright.async_api import Page

from models.product import Product
from core.network_interceptor import NetworkInterceptor
from core.browser import BrowserManager
from utils.config_manager import ConfigManager
from utils.logger import get_logger
from utils.anti_detect import human_delay, simulate_scroll
import utils.taobao_selectors as selectors


class ProductScraper:
    """商品信息采集"""

    def __init__(self, browser: BrowserManager, config: ConfigManager, log=None):
        self._browser = browser
        self._config = config
        self._log = log or get_logger()
        self._interceptor = NetworkInterceptor()
        self._dom_fallback = False

    async def scrape(self, url: str) -> Product:
        """采集商品信息"""
        product = Product(source_url=url)
        product.item_id = self._extract_item_id(url)

        page = self._browser.page
        if not page:
            raise RuntimeError("浏览器未启动")

        # 重置拦截器
        self._interceptor.reset()
        self._dom_fallback = False

        # 开始监听网络
        await self._interceptor.start(page)

        # 导航到商品页面
        self._log.info(f"正在访问: {url}")
        await self._browser.navigate(url)

        # 检测是否被重定向到登录页
        current_url = page.url
        self._log.info(f"当前页面: {current_url}")
        if await self._browser.is_login_page():
            self._log.warning("检测到登录页面，需要先登录淘宝账号")
            product.status = "failed"
            product.error_message = "需要登录淘宝账号，请通过菜单「工具 → 登录检测」完成登录后再试"
            return product

        # 等待页面加载
        timeout = self._config.get("scraping", "api_wait_timeout", 15000) / 1000
        api_data = await self._interceptor.wait_for_detail(timeout=timeout)

        if api_data:
            self._log.info("API数据拦截成功，解析中...")
            parsed = await self._interceptor.parse_detail_response(api_data)
            self._apply_api_data(product, parsed)
        else:
            self._log.warning("API拦截超时，将使用DOM解析")
            self._dom_fallback = True

        # DOM解析补充/兜底
        if self._dom_fallback or not product.title:
            self._log.info("使用DOM解析商品信息...")
            await self._scrape_from_dom(page, product)

        # 页面title兜底：从<title>标签提取商品标题
        if not product.title:
            page_title = await page.title()
            if page_title:
                # 淘宝页面title格式: "商品标题-tmall.com天猫" 或 "商品标题-淘宝网"
                title = page_title.split("-")[0].strip()
                if title and len(title) > 2:
                    product.title = title
                    self._log.info(f"从页面标题提取到商品名: {product.title}")

        # 模拟滚动加载图片
        await simulate_scroll(page, 500)
        await human_delay(0.5, 1.5)

        # 如果没有图片，尝试从DOM获取
        if not product.original_images:
            product.original_images = await self._scrape_images_from_dom(page)

        # 设置状态
        if product.title:
            product.status = "scraped"
            self._log.info(f"采集成功: {product.display_title}")
        else:
            product.status = "failed"
            product.error_message = "未能获取商品标题"
            self._log.error("采集失败: 未获取到商品标题")
            self._log.info(f"页面URL: {page.url}")
            self._log.info(f"页面标题: {await page.title()}")

        return product

    def _extract_item_id(self, url: str) -> str:
        """从URL提取商品ID"""
        patterns = [
            r'[?&]id=(\d+)',
            r'/item/(\d+)',
            r'/i(\d+)\.htm',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    def _apply_api_data(self, product: Product, data: dict):
        """将API数据写入Product"""
        if data.get("title"):
            product.title = data["title"]
        if data.get("item_id"):
            product.item_id = data["item_id"]
        if data.get("price"):
            product.price = data["price"]
        if data.get("images"):
            product.original_images = data["images"]
        if data.get("sku_list"):
            product.sku_list = data["sku_list"]
        if data.get("attributes"):
            product.attributes = data["attributes"]
        if data.get("shop_name"):
            product.shop_name = data["shop_name"]
        if data.get("sales_count"):
            product.sales_count = str(data["sales_count"])

    async def _scrape_from_dom(self, page: Page, product: Product):
        """从DOM解析商品信息（兜底方案）"""
        # 标题
        if not product.title:
            product.title = await self._try_selectors_text(
                page, selectors.TITLE_SELECTORS, "商品标题"
            )

        # 价格
        if product.price <= 0:
            price_text = await self._try_selectors_text(
                page, selectors.PRICE_SELECTORS, "价格"
            )
            if price_text:
                try:
                    product.price = float(re.sub(r'[^\d.]', '', price_text))
                except ValueError:
                    pass

        # 店铺名
        if not product.shop_name:
            product.shop_name = await self._try_selectors_text(
                page, selectors.SHOP_NAME_SELECTORS, "店铺名"
            )

        # 属性
        if not product.attributes:
            product.attributes = await self._scrape_attributes_from_dom(page)

    async def _try_selectors_text(self, page: Page, selector_list: list, label: str) -> str:
        """依次尝试选择器列表，返回第一个匹配的文本"""
        for selector in selector_list:
            try:
                el = page.locator(selector).first
                if await el.is_visible(timeout=2000):
                    text = await el.text_content(timeout=2000)
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return ""

    async def _scrape_images_from_dom(self, page: Page) -> list:
        """从DOM提取商品图片URL"""
        images = []
        for selector in selectors.MAIN_IMAGE_SELECTORS:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                for i in range(min(count, 10)):
                    src = await elements.nth(i).get_attribute("src", timeout=1000)
                    if src:
                        if src.startswith("//"):
                            src = "https:" + src
                        # 去掉缩略参数获取大图
                        src = re.sub(r'_\d+x\d+\.\w+$', '', src)
                        src = re.sub(r'\?.*$', '', src)
                        if src not in images:
                            images.append(src)
                if images:
                    break
            except Exception:
                continue
        return images

    async def _scrape_attributes_from_dom(self, page: Page) -> dict:
        """从DOM解析商品属性"""
        attrs = {}
        for selector in selectors.ATTRIBUTE_SELECTORS:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                if count == 0:
                    continue
                for i in range(count):
                    text = await elements.nth(i).text_content(timeout=1000)
                    if text and ":" in text:
                        parts = text.split(":", 1)
                        attrs[parts[0].strip()] = parts[1].strip()
                    elif text and "：" in text:
                        parts = text.split("：", 1)
                        attrs[parts[0].strip()] = parts[1].strip()
                if attrs:
                    break
            except Exception:
                continue
        return attrs
