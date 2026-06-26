"""
登录对话框
当检测到淘宝未登录时弹出，引导用户扫码或手动登录
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
)
from PySide6.QtCore import Qt, Signal, QTimer


class LoginDialog(QDialog):
    """淘宝登录等待对话框"""

    login_success = Signal()

    def __init__(self, parent=None, login_url: str = "https://login.taobao.com"):
        super().__init__(parent)
        self._login_url = login_url
        self._check_timer = QTimer(self)
        self._is_checking = False
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("淘宝登录")
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 图标和标题
        title = QLabel("🔐 需要登录淘宝账号")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 说明文字
        info = QLabel(
            "浏览器已打开淘宝登录页面，请在浏览器中完成登录操作。\n"
            "支持扫码登录或账号密码登录。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 13px; line-height: 1.6;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # 状态提示
        self._status_label = QLabel("⏳ 等待登录中...")
        self._status_label.setStyleSheet("color: #4285f4; font-size: 13px; font-weight: bold;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        # 按钮区
        btn_layout = QHBoxLayout()
        self._btn_check = QPushButton("我已登录，检测")
        self._btn_check.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3367d6; }
        """)
        self._btn_check.clicked.connect(self._on_check)

        self._btn_cancel = QPushButton("取消")
        self._btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #666;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e8e8e8; }
        """)
        self._btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_cancel)
        btn_layout.addWidget(self._btn_check)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _on_check(self):
        """用户点击检测按钮"""
        self._status_label.setText("🔄 正在检测登录状态...")
        self._status_label.setStyleSheet("color: #e6a100; font-size: 13px; font-weight: bold;")
        self._btn_check.setEnabled(False)
        self.login_success.emit()

    def set_login_result(self, success: bool):
        """外部调用：设置登录检测结果"""
        if success:
            self._status_label.setText("✅ 登录成功！")
            self._status_label.setStyleSheet("color: #3cb44b; font-size: 13px; font-weight: bold;")
            QTimer.singleShot(800, self.accept)
        else:
            self._status_label.setText("❌ 未检测到登录，请重试")
            self._status_label.setStyleSheet("color: #dc3c32; font-size: 13px; font-weight: bold;")
            self._btn_check.setEnabled(True)
