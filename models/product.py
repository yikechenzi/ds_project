"""
商品数据模型
所有模块之间的数据通信通过此数据结构完成
"""
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class SkuItem:
    """SKU规格项"""
    name: str = ""              # SKU名称, 如 "Deepin单系统/16G"
    price: float = 0.0          # 价格
    stock: int = 100            # 库存
    sku_code: str = ""          # SKU编码
    prop_path: str = ""         # 属性路径


@dataclass
class Product:
    """商品数据模型 - 采集和上架的核心数据结构"""
    source_url: str = ""              # 来源URL
    item_id: str = ""                 # 商品ID
    title: str = ""                   # 商品标题
    price: float = 0.0                # 商品价格
    original_price: float = 0.0       # 原价
    original_images: list = field(default_factory=list)   # 原始图片URL列表
    local_images: list = field(default_factory=list)       # 本地图片路径列表
    sku_list: list = field(default_factory=list)           # SKU列表 (SkuItem dicts)
    attributes: dict = field(default_factory=dict)         # 商品属性
    description_html: str = ""        # 商品描述HTML
    description_text: str = ""        # 商品描述纯文本
    category: str = ""                # 商品类目
    category_path: list = field(default_factory=list)      # 类目路径
    shop_name: str = ""               # 店铺名称
    sales_count: str = ""             # 销量
    status: str = "pending"           # 状态: pending/scraped/uploading/uploaded/failed
    error_message: str = ""           # 错误信息

    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """从字典创建"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Product":
        """从JSON字符串创建"""
        return cls.from_dict(json.loads(json_str))

    def save_cache(self, cache_dir: str):
        """保存到缓存文件"""
        os.makedirs(cache_dir, exist_ok=True)
        filepath = os.path.join(cache_dir, f"{self.item_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load_cache(cls, cache_dir: str, item_id: str) -> Optional["Product"]:
        """从缓存文件加载"""
        filepath = os.path.join(cache_dir, f"{item_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return cls.from_json(f.read())
        return None

    def validate(self) -> list:
        """校验商品数据, 返回错误列表"""
        errors = []
        if not self.title:
            errors.append("商品标题不能为空")
        if len(self.title) > 60:
            errors.append(f"商品标题过长（{len(self.title)}/60字符）")
        if self.price <= 0:
            errors.append("商品价格必须大于0")
        if not self.original_images and not self.local_images:
            errors.append("至少需要一张商品图片")
        return errors

    @property
    def display_title(self) -> str:
        """显示用的标题（截断）"""
        if len(self.title) > 30:
            return self.title[:30] + "..."
        return self.title

    @property
    def has_images(self) -> bool:
        return bool(self.original_images or self.local_images)
