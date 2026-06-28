"""
采集页面
输入淘宝商品URL，启动采集，显示进度
"""
import re
import asyncio
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFrame,
)
from PySide6.QtCore import Qt, Signal, QThread, Slot

from gui.widgets.log_console import LogConsole


class _ScrapeWorker(QThread):
    """后台采集线程"""
    finished = Signal(object)  # Product or None
    error = Signal(str)

    def __init__(self, scraper, image_manager, url, async_loop, parent=None):
        super().__init__(parent)
        self._scraper = scraper
        self._image_manager = image_manager
        self._url = url
        self._async_loop = async_loop

    def run(self):
        try:
            async def _scrape():
                product = await self._scraper.scrape(self._url)
                if product.original_images:
                    local = await self._image_manager.download_images(
                        product.original_images, product.item_id
                    )
                    product.local_images = local
                return product

            future = asyncio.run_coroutine_threadsafe(_scrape(), self._async_loop)
            product = future.result(timeout=120)
            self.finished.emit(product)
        except Exception as e:
            self.error.emit(str(e))


class UrlInputPage(QWidget):
    """采集页面：输入URL → 采集商品信息"""

    # 采集完成信号，携带Product对象
    scrape_completed = Signal(object)
    navigate_to_review = Signal()
    # 请求初始化浏览器（按需启动）
    request_browser_init = Signal(str)

    def __init__(self, scraper, image_manager, async_loop=None, log=None, parent=None):
        super().__init__(parent)
        self._scraper = scraper
        self._image_manager = image_manager
        self._async_loop = async_loop
        self._log = log
        self._worker = None
        self._pending_url = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题
        title = QLabel("🔍 商品采集")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # URL输入区
        input_group = QGroupBox("商品链接")
        input_layout = QHBoxLayout(input_group)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("请粘贴淘宝商品链接，如 https://item.taobao.com/item.htm?id=xxx")
        self._url_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #4285f4; }
        """)
        self._url_input.returnPressed.connect(self._on_scrape)

        self._btn_scrape = QPushButton("开始采集")
        self._btn_scrape.setStyleSheet("""
            QPushButton {
                background-color: #4285f4; color: white;
                border: none; border-radius: 8px;
                padding: 12px 28px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3367d6; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        self._btn_scrape.clicked.connect(self._on_scrape)

        self._status_label = QLabel("💡 输入链接后点击开始采集，浏览器将自动启动")
        self._status_label.setStyleSheet("color: #666; font-size: 13px;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        input_layout.addWidget(self._url_input)
        input_layout.addWidget(self._btn_scrape)
        layout.addWidget(input_group)
        layout.addWidget(self._status_label)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #eee;")
        layout.addWidget(sep)

        # 日志面板
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        self._log_console = LogConsole()
        log_layout.addWidget(self._log_console)
        layout.addWidget(log_group, stretch=1)

    def _on_scrape(self):
        url = self._url_input.text().strip()
        if not url:
            self._log_console.append_log("WARNING", "请输入商品链接")
            return
        if not re.search(r'taobao\.com|tmall\.com', url):
            self._log_console.append_log("WARNING", "请输入有效的淘宝/天猫链接")
            return
        if not self._scraper:
            # 浏览器未就绪，先启动浏览器，采集会在就绪后自动执行
            self._pending_url = url
            self._btn_scrape.setEnabled(False)
            self._btn_scrape.setText("正在启动浏览器...")
            self._status_label.setText("⏳ 正在启动浏览器，请稍候...")
            self._status_label.setStyleSheet("color: #e6a100; font-size: 13px;")
            self._log_console.append_log("INFO", "正在启动浏览器引擎...")
            self.request_browser_init.emit(url)
            return

        self._start_scrape(url)

    @Slot(object)
    def _on_finished(self, product):
        self._btn_scrape.setEnabled(True)
        self._btn_scrape.setText("开始采集")
        if product and product.status == "scraped":
            self._log_console.append_log("INFO", f"✅ 采集成功: {product.display_title}")
            self._log_console.append_log("INFO", f"  价格: ¥{product.price}")
            self._log_console.append_log("INFO", f"  图片: {len(product.original_images)} 张")
            self._log_console.append_log("INFO", f"  SKU: {len(product.sku_list)} 个")
            self.scrape_completed.emit(product)
            self.navigate_to_review.emit()
        else:
            msg = product.error_message if product else "未知错误"
            self._log_console.append_log("ERROR", f"❌ 采集失败: {msg}")

    @Slot(str)
    def _on_error(self, error_msg):
        self._btn_scrape.setEnabled(True)
        self._btn_scrape.setText("开始采集")
        self._log_console.append_log("ERROR", f"❌ 采集出错: {error_msg}")

    def set_engine_ready(self):
        """浏览器引擎就绪后调用，启用采集按钮"""
        self._btn_scrape.setEnabled(True)
        self._btn_scrape.setText("开始采集")
        self._status_label.setText("✅ 浏览器已就绪，可以开始采集")
        self._status_label.setStyleSheet("color: #3cb44b; font-size: 13px;")
        # 如果有待执行的采集任务，自动开始
        if self._pending_url:
            url = self._pending_url
            self._pending_url = None
            self._url_input.setText(url)
            self._start_scrape(url)

    def _start_scrape(self, url: str):
        """执行采集"""
        self._btn_scrape.setEnabled(False)
        self._btn_scrape.setText("采集中...")
        self._log_console.append_log("INFO", f"开始采集: {url[:60]}...")

        self._worker = _ScrapeWorker(self._scraper, self._image_manager, url, self._async_loop, self)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def get_log_console(self) -> LogConsole:
        return self._log_console
