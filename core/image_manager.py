"""
图片管理器
负责商品图片的下载、处理和格式转换
"""
import asyncio
import os
import re
from typing import Optional
from io import BytesIO

import httpx
from PIL import Image

from utils.config_manager import ConfigManager
from utils.logger import get_logger


class ImageManager:
    """图片下载与处理"""

    def __init__(self, config: ConfigManager, log=None):
        self._config = config
        self._log = log or get_logger()
        self._images_dir = config.get("paths", "images_dir", "data/images")
        self._min_width = config.get("images", "min_width", 800)
        self._min_height = config.get("images", "min_height", 800)
        self._max_main = config.get("images", "max_main_images", 5)
        self._jpeg_quality = config.get("images", "jpeg_quality", 90)
        self._timeout = config.get("images", "download_timeout", 15000) / 1000

    async def download_images(self, image_urls: list, item_id: str) -> list:
        """下载商品图片，返回本地路径列表"""
        if not image_urls:
            return []

        save_dir = os.path.join(self._images_dir, item_id)
        os.makedirs(save_dir, exist_ok=True)

        local_paths = []
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            tasks = []
            for i, url in enumerate(image_urls[:self._max_main]):
                tasks.append(self._download_one(client, url, save_dir, i))
            results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, str) and r:
                local_paths.append(r)
            elif isinstance(r, Exception):
                self._log.warning(f"图片下载失败: {r}")

        self._log.info(f"已下载 {len(local_paths)}/{len(image_urls)} 张图片")
        return local_paths

    async def _download_one(self, client: httpx.AsyncClient, url: str, save_dir: str, index: int) -> Optional[str]:
        """下载单张图片"""
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            img_data = resp.content

            # 打开图片检查尺寸
            img = Image.open(BytesIO(img_data))
            w, h = img.size

            # 如果太小，尝试替换URL中的尺寸参数获取大图
            if w < self._min_width or h < self._min_height:
                big_url = self._try_get_big_url(url)
                if big_url and big_url != url:
                    try:
                        resp2 = await client.get(big_url)
                        resp2.raise_for_status()
                        img = Image.open(BytesIO(resp2.content))
                        w, h = img.size
                        if w >= self._min_width and h >= self._min_height:
                            img_data = resp2.content
                    except Exception:
                        pass

            # 转为RGB并保存为JPEG
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            filename = f"main_{index}.jpg"
            filepath = os.path.join(save_dir, filename)
            img.save(filepath, "JPEG", quality=self._jpeg_quality)
            return filepath
        except Exception as e:
            raise RuntimeError(f"下载图片失败 [{url[:60]}...]: {e}")

    def _try_get_big_url(self, url: str) -> str:
        """尝试从缩略图URL获取原图URL"""
        # 去掉淘宝的尺寸后缀，如 _300x300.jpg
        cleaned = re.sub(r'_\d+x\d+\.\w+', '', url)
        # 去掉查询参数
        cleaned = re.sub(r'\?.*$', '', cleaned)
        # 确保有后缀
        if not re.search(r'\.(jpg|jpeg|png|webp)$', cleaned, re.I):
            cleaned += '.jpg'
        return cleaned

    def get_local_path(self, item_id: str, index: int = 0) -> Optional[str]:
        """获取已下载图片的本地路径"""
        path = os.path.join(self._images_dir, item_id, f"main_{index}.jpg")
        if os.path.exists(path):
            return path
        return None

    def cleanup(self, item_id: str):
        """清理指定商品的图片缓存"""
        import shutil
        dir_path = os.path.join(self._images_dir, item_id)
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            self._log.info(f"已清理图片缓存: {item_id}")
