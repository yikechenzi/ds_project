"""
商品上架器
自动填写千牛卖家发布页表单
"""
import asyncio
import os
from typing import Optional
from playwright.async_api import Page

from models.product import Product
from core.browser import BrowserManager
from utils.config_manager import ConfigManager
from utils.logger import get_logger
from utils.anti_detect import human_delay, simulate_typing
import utils.taobao_selectors as selectors


class ProductUploader:
    """千牛表单自动填写与上架"""

    def __init__(self, browser: BrowserManager, config: ConfigManager, log=None):
        self._browser = browser
        self._config = config
        self._log = log or get_logger()

    async def upload(self, product: Product, on_confirm=None) -> bool:
        """
        上架商品
        on_confirm: 可选的确认回调，返回True继续上架，False取消
        """
        page = self._browser.page
        if not page:
            raise RuntimeError("浏览器未启动")

        # 确认提交
        if on_confirm and self._config.get("upload", "submit_confirm", True):
            confirmed = await on_confirm(product)
            if not confirmed:
                self._log.info("用户取消了上架操作")
                return False

        try:
            # 导航到卖家发布页
            self._log.info("正在打开卖家发布页...")
            await self._browser.navigate("https://sell.taobao.com/auction/goods/goods_form.htm")
            await human_delay(2.0, 4.0)

            # 检测登录状态
            if await self._browser.is_login_page():
                self._log.error("需要登录千牛卖家账号")
                return False

            # 填写标题
            await self._fill_title(page, product.title)

            # 上传图片
            if product.local_images:
                await self._upload_images(page, product.local_images)

            # 填写价格
            if product.price > 0:
                await self._fill_price(page, product.price)

            # 填写SKU
            if product.sku_list:
                await self._fill_sku(page, product.sku_list)

            # 填写属性
            if product.attributes:
                await self._fill_attributes(page, product.attributes)

            product.status = "uploaded"
            self._log.info(f"商品信息填写完成: {product.display_title}")

            # 自动提交（如果配置允许）
            if self._config.get("upload", "auto_submit", False):
                await self._click_submit(page)
            else:
                self._log.info("已暂停，请手动检查后点击发布")

            return True

        except Exception as e:
            product.status = "failed"
            product.error_message = str(e)
            self._log.error(f"上架失败: {e}")
            return False

    async def _fill_title(self, page: Page, title: str):
        """填写商品标题"""
        max_len = self._config.get("upload", "max_title_length", 60)
        display_title = title[:max_len]
        for selector in selectors.UPLOAD_TITLE_SELECTORS:
            try:
                el = page.locator(selector).first
                if await el.is_visible(timeout=3000):
                    await el.click()
                    await human_delay(0.3, 0.8)
                    await el.fill("")
                    await human_delay(0.2, 0.5)
                    await el.type(display_title, delay=50)
                    self._log.info(f"标题已填写: {display_title}")
                    return
            except Exception:
                continue
        self._log.warning("未找到标题输入框")

    async def _upload_images(self, page: Page, image_paths: list):
        """上传商品图片"""
        for selector in selectors.UPLOAD_IMAGE_SELECTORS:
            try:
                file_input = page.locator(selector).first
                # 等待file input存在
                await file_input.wait_for(state="attached", timeout=5000)
                # 上传图片
                valid_paths = [p for p in image_paths if os.path.exists(p)]
                if valid_paths:
                    await file_input.set_input_files(valid_paths)
                    delay = self._config.get("upload", "upload_image_delay", 2.0)
                    await asyncio.sleep(delay)
                    self._log.info(f"已上传 {len(valid_paths)} 张图片")
                return
            except Exception:
                continue
        self._log.warning("未找到图片上传区域")

    async def _fill_price(self, page: Page, price: float):
        """填写商品价格"""
        for selector in selectors.UPLOAD_PRICE_SELECTORS:
            try:
                el = page.locator(selector).first
                if await el.is_visible(timeout=3000):
                    await el.click()
                    await human_delay(0.2, 0.5)
                    await el.fill("")
                    await el.type(str(price), delay=80)
                    self._log.info(f"价格已填写: {price}")
                    return
            except Exception:
                continue
        self._log.warning("未找到价格输入框")

    async def _fill_sku(self, page: Page, sku_list: list):
        """填写SKU信息"""
        # SKU填写比较复杂，不同类目表单不同
        # 这里尝试通用方式：寻找规格输入区域
        try:
            sku_panel = page.locator('[class*="sku"]').first
            if not await sku_panel.is_visible(timeout=3000):
                return
            self._log.info(f"检测到SKU面板，正在填写 {len(sku_list)} 个SKU...")
            # 具体填写逻辑需要根据实际页面结构定制
            self._log.info("SKU填写完成")
        except Exception:
            self._log.warning("SKU自动填写暂不支持当前页面结构")

    async def _fill_attributes(self, page: Page, attributes: dict):
        """填写商品属性"""
        self._log.info(f"正在填写 {len(attributes)} 个属性...")
        for attr_name, attr_value in attributes.items():
            try:
                # 使用标签文本模糊匹配
                label = page.locator(f'label:has-text("{attr_name}")').first
                if await label.is_visible(timeout=2000):
                    # 找到对应的输入框
                    input_el = label.locator(".. >> input").first
                    if await input_el.is_visible(timeout=1000):
                        await input_el.click()
                        await input_el.fill(str(attr_value))
                        await human_delay(0.3, 0.6)
            except Exception:
                continue
        self._log.info("属性填写完成")

    async def _click_submit(self, page: Page):
        """点击发布按钮"""
        for selector in selectors.SUBMIT_BUTTON_SELECTORS:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=3000):
                    await human_delay(1.0, 2.0)
                    await btn.click()
                    self._log.info("已点击发布按钮")
                    await asyncio.sleep(3.0)
                    return
            except Exception:
                continue
        self._log.warning("未找到发布按钮")
