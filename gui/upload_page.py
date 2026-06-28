"""
上架页面
自动填写千牛表单并提交，实时显示进度和日志
"""
import asyncio
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QFrame,
)
from PySide6.QtCore import Qt, Signal, QThread, Slot

from gui.widgets.log_console import LogConsole
from gui.widgets.progress_indicator import ProgressIndicator
from models.product import Product


class _UploadWorker(QThread):
    """后台上架线程"""
    finished = Signal(bool)
    error = Signal(str)

    def __init__(self, uploader, product, async_loop, parent=None):
        super().__init__(parent)
        self._uploader = uploader
        self._product = product
        self._async_loop = async_loop

    def run(self):
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._uploader.upload(self._product), self._async_loop
            )
            result = future.result(timeout=300)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class UploadPage(QWidget):
    """上架页面：执行自动上架"""

    upload_finished = Signal(bool)
    back_clicked = Signal()

    def __init__(self, uploader, async_loop=None, parent=None):
        super().__init__(parent)
        self._uploader = uploader
        self._async_loop = async_loop
        self._product = None
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题
        title = QLabel("🚀 商品上架")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # 进度指示器
        self._progress = ProgressIndicator(["采集", "审核", "上架"])
        self._progress.set_current(2)  # 在上架步骤
        layout.addWidget(self._progress)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #eee;")
        layout.addWidget(sep)

        # 商品摘要
        summary_group = QGroupBox("上架信息")
        summary_layout = QVBoxLayout(summary_group)
        self._title_label = QLabel("标题：-")
        self._title_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        self._title_label.setWordWrap(True)
        summary_layout.addWidget(self._title_label)

        self._price_label = QLabel("价格：-")
        self._price_label.setStyleSheet("font-size: 13px; color: #e65100;")
        summary_layout.addWidget(self._price_label)

        self._sku_label = QLabel("SKU：-")
        self._sku_label.setStyleSheet("font-size: 13px; color: #666;")
        summary_layout.addWidget(self._sku_label)

        self._images_label = QLabel("图片：-")
        self._images_label.setStyleSheet("font-size: 13px; color: #666;")
        summary_layout.addWidget(self._images_label)
        layout.addWidget(summary_group)

        # 提交选项
        self._auto_check = QCheckBox("自动提交发布（不推荐，建议手动检查后发布）")
        self._auto_check.setStyleSheet("color: #dc3c32; font-size: 12px;")
        layout.addWidget(self._auto_check)

        # 按钮
        btn_layout = QHBoxLayout()
        self._btn_back = QPushButton("← 返回审核")
        self._btn_back.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5; color: #666;
                border: 1px solid #ddd; border-radius: 6px;
                padding: 10px 20px; font-size: 13px;
            }
            QPushButton:hover { background-color: #e8e8e8; }
        """)
        self._btn_back.clicked.connect(self.back_clicked.emit)

        self._btn_upload = QPushButton("开始上架")
        self._btn_upload.setStyleSheet("""
            QPushButton {
                background-color: #3cb44b; color: white;
                border: none; border-radius: 8px;
                padding: 12px 32px; font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2d963a; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        self._btn_upload.clicked.connect(self._on_upload)

        btn_layout.addWidget(self._btn_back)
        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_upload)
        layout.addLayout(btn_layout)

        # 日志面板
        log_group = QGroupBox("上架日志")
        log_layout = QVBoxLayout(log_group)
        self._log_console = LogConsole()
        log_layout.addWidget(self._log_console)
        layout.addWidget(log_group, stretch=1)

    def set_product(self, product: Product):
        """设置要上架的商品"""
        self._product = product
        self._title_label.setText(f"标题：{product.title}")
        self._price_label.setText(f"价格：¥{product.price}")
        self._sku_label.setText(f"SKU：{len(product.sku_list)} 个规格")
        self._images_label.setText(f"图片：{len(product.local_images)} 张")

    def _on_upload(self):
        if not self._product:
            return
        self._btn_upload.setEnabled(False)
        self._btn_upload.setText("上架中...")
        self._log_console.append_log("INFO", "开始上架流程...")

        self._worker = _UploadWorker(self._uploader, self._product, self._async_loop, self)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @Slot(bool)
    def _on_finished(self, success):
        self._btn_upload.setEnabled(True)
        self._btn_upload.setText("开始上架")
        if success:
            self._log_console.append_log("INFO", "✅ 上架操作完成！")
            self._progress.complete_current()
        else:
            self._log_console.append_log("ERROR", "❌ 上架失败")
        self.upload_finished.emit(success)

    @Slot(str)
    def _on_error(self, msg):
        self._btn_upload.setEnabled(True)
        self._btn_upload.setText("开始上架")
        self._log_console.append_log("ERROR", f"❌ 上架出错: {msg}")
        self.upload_finished.emit(False)

    def get_log_console(self) -> LogConsole:
        return self._log_console
