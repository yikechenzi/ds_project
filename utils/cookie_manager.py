"""
Cookie管理器
保存和加载Playwright浏览器的Cookie
"""
import json
import os
from typing import Optional


class CookieManager:
    """Cookie持久化管理"""

    @staticmethod
    async def save_cookies(context, filepath: str):
        """保存Cookie到JSON文件"""
        cookies = await context.cookies()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

    @staticmethod
    async def load_cookies(context, filepath: str) -> bool:
        """从JSON文件加载Cookie"""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            if cookies:
                await context.add_cookies(cookies)
                return True
        except (json.JSONDecodeError, Exception):
            pass
        return False

    @staticmethod
    def has_saved_cookies(filepath: str) -> bool:
        """检查是否有保存的Cookie"""
        return os.path.exists(filepath) and os.path.getsize(filepath) > 10
