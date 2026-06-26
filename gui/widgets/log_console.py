"""
日志面板组件
实时显示日志输出，支持不同级别着色
"""
from datetime import datetime
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor


class LogConsole(QWidget):
    """日志输出面板"""

    LEVEL_COLORS = {
        "DEBUG": QColor(128, 128, 128),
        "INFO": QColor(60, 180, 75),
        "WARNING": QColor(230, 180, 50),
        "ERROR": QColor(220, 60, 50),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._max_lines = 1000
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 工具栏
        toolbar = QHBoxLayout()
        self._btn_clear = QPushButton("清空")
        self._btn_clear.setFixedWidth(60)
        self._btn_clear.clicked.connect(self._clear)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_clear)
        layout.addLayout(toolbar)

        # 日志文本框
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setMaximumBlockCount(self._max_lines)
        self._text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        layout.addWidget(self._text)

    @Slot(str, str)
    def append_log(self, level: str, message: str):
        """追加日志消息"""
        color = self.LEVEL_COLORS.get(level, QColor(200, 200, 200))
        timestamp = datetime.now().strftime("%H:%M:%S")

        fmt = QTextCharFormat()
        fmt.setForeground(color)

        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(f"[{timestamp}] [{level}] {message}\n", fmt)
        self._text.setTextCursor(cursor)
        self._text.ensureCursorVisible()

    def _clear(self):
        """清空日志"""
        self._text.clear()

    def get_text(self) -> str:
        """获取全部日志文本"""
        return self._text.toPlainText()
