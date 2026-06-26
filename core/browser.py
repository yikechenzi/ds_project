"""
浏览器管理器
负责 Playwright 浏览器的启动、登录状态管理、反检测
"""
import asyncio
import os
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from utils.config_manager import ConfigManager
from utils.cookie_manager import CookieManager
from utils.anti_detect import get_stealth_init_script, human_delay
from utils.taobao_selectors import LOGIN_CHECK_SELECTORS, LOGIN_PAGE_SELECTORS
from utils.logger import get_logger


class BrowserManager:
    """浏览器生命周期管理"""

    def __init__(self, config: ConfigManager, log=None):
        self._config = config
        self._log = log or get_logger()
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def start(self, headless: bool = False) -> Page:
        """启动浏览器，返回主页面"""
        browser_cfg = self._config.get("browser") or {}

        self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=headless,
            slow_mo=browser_cfg.get("slow_mo", 100),
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        user_data_dir = browser_cfg.get("user_data_dir", "data/browser_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        self._context = await self._browser.new_context(
            viewport={
                "width": browser_cfg.get("viewport_width", 1366),
                "height": browser_cfg.get("viewport_height", 768),
            },
            locale=browser_cfg.get("locale", "zh-CN"),
            timezone_id=browser_cfg.get("timezone", "Asia/Shanghai"),
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        # 注入反检测脚本
        await self._context.add_init_script(get_stealth_init_script())

        # 尝试加载Cookie
        cookie_path = self._config.get("paths", "cookies_file", "data/cookies/session.json")
        loaded = await CookieManager.load_cookies(self._context, cookie_path)
        if loaded:
            self._log.info("已加载保存的Cookie")

        self._page = await self._context.new_page()
        self._log.info("浏览器启动完成")
        return self._page

    @property
    def page(self) -> Optional[Page]:
        return self._page

    @property
    def context(self) -> Optional[BrowserContext]:
        return self._context

    async def navigate(self, url: str, timeout: float = 30000):
        """导航到指定URL"""
        if not self._page:
            raise RuntimeError("浏览器未启动")
        await self._page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        await human_delay(1.0, 2.0)

    async def is_logged_in(self) -> bool:
        """检测淘宝登录状态"""
        if not self._page:
            return False
        try:
            for selector in LOGIN_CHECK_SELECTORS:
                el = self._page.locator(selector).first
                if await el.is_visible(timeout=1000):
                    return True
        except Exception:
            pass
        return False

    async def is_login_page(self) -> bool:
        """检测是否在登录页面"""
        if not self._page:
            return False
        try:
            for selector in LOGIN_PAGE_SELECTORS:
                el = self._page.locator(selector).first
                if await el.is_visible(timeout=1000):
                    return True
        except Exception:
            pass
        return False

    async def save_cookies(self):
        """保存当前Cookie"""
        if not self._context:
            return
        cookie_path = self._config.get("paths", "cookies_file", "data/cookies/session.json")
        os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
        await CookieManager.save_cookies(self._context, cookie_path)
        self._log.info("Cookie已保存")

    async def close(self):
        """关闭浏览器"""
        try:
            if self._context:
                await self.save_cookies()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self._log.info("浏览器已关闭")
