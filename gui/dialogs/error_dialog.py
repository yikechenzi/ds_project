"""
错误提示对话框
显示错误详情，支持重试操作
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame,
)
from PySide6.QtCore import Qt, Signal


class ErrorDialog(QDialog):
    """错误提示弹窗"""

    retry_requested = Signal()

    def __init__(self, title: str, message: str, detail: str = "", parent=None):
        super().__init__(parent)
        self._title = title
        self._message = message
        self._detail = detail
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("错误")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 图标和标题
        header = QLabel(f"❌ {self._title}")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #dc3c32;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #eee;")
        layout.addWidget(sep)

        # 消息
        msg = QLabel(self._message)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(msg)

        # 详情（可展开）
        if self._detail:
            detail_edit = QTextEdit()
            detail_edit.setPlainText(self._detail)
            detail_edit.setReadOnly(True)
            detail_edit.setMaximumHeight(120)
            detail_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-family: Consolas, monospace;
                    font-size: 11px;
                    color: #666;
                }
            """)
            layout.addWidget(detail_edit)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5; color: #666;
                border: 1px solid #ddd; border-radius: 6px;
                padding: 8px 24px; font-size: 13px;
            }
            QPushButton:hover { background-color: #e8e8e8; }
        """)
        btn_close.clicked.connect(self.reject)

        btn_retry = QPushButton("重试")
        btn_retry.setStyleSheet("""
            QPushButton {
                background-color: #4285f4; color: white;
                border: none; border-radius: 6px;
                padding: 8px 24px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3367d6; }
        """)
        btn_retry.clicked.connect(self._on_retry)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(btn_retry)
        layout.addLayout(btn_layout)

    def _on_retry(self):
        self.retry_requested.emit()
        self.accept()

    @staticmethod
    def show_error(title: str, message: str, detail: str = "", parent=None) -> bool:
        """
        静态方法：显示错误弹窗
        返回 True 表示用户点击了重试
        """
        dlg = ErrorDialog(title, message, detail, parent)
        result = dlg.exec()
        return result == QDialog.DialogCode.Accepted
