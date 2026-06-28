"""
主窗口
组装所有页面，管理页面切换和核心流程
"""
import asyncio
import threading
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMenuBar, QStatusBar, QToolBar,
    QLabel, QApplication, QMessageBox,
)
from PySide6.QtCore import Qt, Slot, QTimer, Signal
from PySide6.QtGui import QAction, QIcon

from gui.url_input_page import UrlInputPage
from gui.review_page import ReviewPage
from gui.upload_page import UploadPage
from gui.dialogs.login_dialog import LoginDialog
from gui.dialogs.settings_dialog import SettingsDialog
from gui.dialogs.error_dialog import ErrorDialog
from gui.widgets.progress_indicator import ProgressIndicator
from gui.widgets.log_console import LogConsole

from core.browser import BrowserManager
from core.scraper import ProductScraper
from core.image_manager import ImageManager
from core.uploader import ProductUploader
from models.product import Product
from utils.config_manager import ConfigManager
from utils.logger import get_logger


class MainWindow(QMainWindow):
    """应用主窗口"""

    # 信号：用于从后台线程通知主线程
    _browser_ready_signal = Signal()
    _browser_failed_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self._config = ConfigManager()
        self._log = get_logger()

        # 持久事件循环（所有 Playwright 异步操作共用）
        self._async_loop = asyncio.new_event_loop()
        self._async_thread: threading.Thread = None

        # 核心引擎
        self._browser = BrowserManager(self._config, self._log)
        self._scraper = None
        self._image_manager = ImageManager(self._config, self._log)
        self._uploader = None

        # 数据
        self._current_product: Product = None

        # 连接信号
        self._browser_ready_signal.connect(self._on_browser_ready)
        self._browser_failed_signal.connect(self._on_browser_failed)

        self._init_ui()
        self._init_engine()

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("淘宝自动上架助手")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)

        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # 顶部进度指示器
        self._progress = ProgressIndicator(["采集", "审核", "上架"])
        main_layout.addWidget(self._progress)

        # 页面栈
        self._stack = QStackedWidget()

        # 创建三个页面
        self._url_page = UrlInputPage(
            scraper=None,
            image_manager=self._image_manager,
            async_loop=self._async_loop,
            log=self._log,
        )
        self._review_page = ReviewPage()
        self._upload_page = UploadPage(uploader=None, async_loop=self._async_loop)

        self._stack.addWidget(self._url_page)   # index 0
        self._stack.addWidget(self._review_page)  # index 1
        self._stack.addWidget(self._upload_page)   # index 2

        main_layout.addWidget(self._stack, stretch=1)

        # 底部日志面板
        self._global_log = LogConsole()
        self._global_log.setMaximumHeight(160)
        main_layout.addWidget(self._global_log)

        # 连接信号
        self._connect_signals()

        # 菜单栏
        self._setup_menu()

        # 状态栏
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("就绪")

    def _setup_menu(self):
        """菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        act_quit = QAction("退出(&Q)", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        act_settings = QAction("设置(&S)", self)
        act_settings.setShortcut("Ctrl+,")
        act_settings.triggered.connect(self._show_settings)
        tools_menu.addAction(act_settings)

        act_login = QAction("登录检测(&L)", self)
        act_login.triggered.connect(self._check_login)
        tools_menu.addAction(act_login)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        act_about = QAction("关于(&A)", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _connect_signals(self):
        """连接页面间信号"""
        # 采集页 → 审核页
        self._url_page.scrape_completed.connect(self._on_scrape_done)
        self._url_page.navigate_to_review.connect(lambda: self._switch_page(1))
        # 按需启动浏览器
        self._url_page.request_browser_init.connect(self._on_request_browser_init)

        # 审核页 → 上架页
        self._review_page.confirm_clicked.connect(self._on_review_confirm)
        self._review_page.back_clicked.connect(lambda: self._switch_page(0))

        # 上架页 → 完成
        self._upload_page.upload_finished.connect(self._on_upload_done)
        self._upload_page.back_clicked.connect(lambda: self._switch_page(1))

    def _init_engine(self):
        """初始化核心引擎 - 启动持久事件循环线程，浏览器按需启动"""
        # 启动持久事件循环线程
        self._async_thread = threading.Thread(target=self._async_loop.run_forever, daemon=True)
        self._async_thread.start()
        self._log.info("持久事件循环已启动")
        self._status.showMessage("就绪 - 浏览器将在采集时自动启动")

    @Slot(str)
    def _on_request_browser_init(self, url: str):
        """收到采集页的浏览器启动请求"""
        self._log.info("正在初始化浏览器引擎...")
        self._status.showMessage("正在启动浏览器...")
        self._do_init_browser()

    def _run_async(self, coro):
        """在线程安全的方式在持久事件循环上执行协程，返回 Future"""
        return asyncio.run_coroutine_threadsafe(coro, self._async_loop)

    def _do_init_browser(self):
        """在持久事件循环上初始化浏览器"""
        async def _init():
            try:
                await self._browser.start(headless=False)
                self._scraper = ProductScraper(self._browser, self._config, self._log)
                self._uploader = ProductUploader(self._browser, self._config, self._log)

                # 注入到页面
                self._url_page._scraper = self._scraper
                self._upload_page._uploader = self._uploader

                self._log.info("浏览器引擎初始化完成")
                self._browser_ready_signal.emit()
            except Exception as e:
                self._log.error(f"浏览器启动失败: {e}")
                self._browser_failed_signal.emit(str(e))

        self._run_async(_init())

    def _switch_page(self, index: int):
        """切换页面"""
        self._stack.setCurrentIndex(index)
        self._progress.set_current(index)
        page_names = {0: "采集", 1: "审核", 2: "上架"}
        self._status.showMessage(f"当前步骤: {page_names.get(index, '')}")

    def _on_browser_ready(self):
        """浏览器初始化成功，通知采集页启用按钮"""
        self._status.showMessage("就绪 - 浏览器已启动")
        self._global_log.append_log("INFO", "✅ 浏览器引擎已就绪")
        self._url_page.set_engine_ready()

    def _on_browser_failed(self, error_msg: str):
        """浏览器初始化失败"""
        self._status.showMessage(f"浏览器启动失败: {error_msg}")
        self._global_log.append_log("ERROR", f"❌ 浏览器启动失败: {error_msg}")
        self._url_page._status_label.setText(f"❌ 浏览器启动失败，请重启程序")
        self._url_page._status_label.setStyleSheet("color: #dc3c32; font-size: 13px;")

    @Slot(object)
    def _on_scrape_done(self, product: Product):
        """采集完成"""
        self._current_product = product
        self._review_page.set_product(product)
        self._log.info(f"商品信息已就绪: {product.display_title}")

    @Slot(object)
    def _on_review_confirm(self, product: Product):
        """审核确认"""
        self._current_product = product
        self._upload_page.set_product(product)
        self._switch_page(2)

    @Slot(bool)
    def _on_upload_done(self, success: bool):
        """上架完成"""
        if success:
            self._progress.complete_current()
            self._log.info("✅ 商品上架成功！")
            self._status.showMessage("上架完成！")
        else:
            self._log.error("❌ 商品上架失败")
            self._status.showMessage("上架失败")

    def _show_settings(self):
        """显示设置对话框"""
        dlg = SettingsDialog(self._config, self)
        dlg.exec()

    def _check_login(self):
        """登录检测"""
        if not self._browser.page:
            QMessageBox.warning(self, "提示", "浏览器尚未启动，请稍候...")
            return

        self._log.info("正在检测登录状态...")
        dlg = LoginDialog(self)

        # 连接检测信号
        dlg.login_success.connect(lambda: self._do_login_check(dlg))
        dlg.exec()

    def _do_login_check(self, dlg: LoginDialog):
        """执行登录检测"""
        def _check():
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self._browser.is_logged_in(), self._async_loop
                )
                logged_in = future.result(timeout=10)
            except Exception:
                logged_in = False
            QTimer.singleShot(0, lambda: dlg.set_login_result(logged_in))
        threading.Thread(target=_check, daemon=True).start()

    def _show_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "<h3>淘宝自动上架助手 v1.0</h3>"
            "<p>从淘宝采集商品信息，自动填写千牛发布表单。</p>"
            "<p>技术栈：PySide6 + Playwright + httpx + Pillow</p>"
        )

    def closeEvent(self, event):
        """窗口关闭事件"""
        self._log.info("正在关闭应用...")
        # 在持久循环上关闭浏览器
        async def _close():
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._async_loop and self._async_loop.is_running():
            future = asyncio.run_coroutine_threadsafe(_close(), self._async_loop)
            try:
                future.result(timeout=5)
            except Exception:
                pass
            self._async_loop.call_soon_threadsafe(self._async_loop.stop)
        event.accept()
