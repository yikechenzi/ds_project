"""
设置对话框
管理浏览器、采集、上传、图片等配置项
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit,
    QLabel, QPushButton, QGroupBox,
)
from PySide6.QtCore import Qt

from utils.config_manager import ConfigManager


class SettingsDialog(QDialog):
    """应用设置对话框"""

    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self._config = config
        self._widgets = {}
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # 标签页
        tabs = QTabWidget()

        # 浏览器标签
        browser_tab = QWidget()
        browser_form = QFormLayout(browser_tab)
        self._widgets["headless"] = QCheckBox("无头模式（隐藏浏览器窗口）")
        browser_form.addRow("运行模式：", self._widgets["headless"])
        self._widgets["slow_mo"] = QSpinBox()
        self._widgets["slow_mo"].setRange(0, 5000)
        self._widgets["slow_mo"].setSuffix(" ms")
        browser_form.addRow("操作间隔：", self._widgets["slow_mo"])
        tabs.addTab(browser_tab, "浏览器")

        # 采集标签
        scrape_tab = QWidget()
        scrape_form = QFormLayout(scrape_tab)
        self._widgets["api_wait_timeout"] = QSpinBox()
        self._widgets["api_wait_timeout"].setRange(1000, 60000)
        self._widgets["api_wait_timeout"].setSuffix(" ms")
        scrape_form.addRow("API等待超时：", self._widgets["api_wait_timeout"])
        self._widgets["scroll_delay_min"] = QDoubleSpinBox()
        self._widgets["scroll_delay_min"].setRange(0.1, 10.0)
        self._widgets["scroll_delay_min"].setSuffix(" 秒")
        scrape_form.addRow("滚动最小延迟：", self._widgets["scroll_delay_min"])
        self._widgets["scroll_delay_max"] = QDoubleSpinBox()
        self._widgets["scroll_delay_max"].setRange(0.1, 10.0)
        self._widgets["scroll_delay_max"].setSuffix(" 秒")
        scrape_form.addRow("滚动最大延迟：", self._widgets["scroll_delay_max"])
        tabs.addTab(scrape_tab, "采集")

        # 上传标签
        upload_tab = QWidget()
        upload_form = QFormLayout(upload_tab)
        self._widgets["auto_submit"] = QCheckBox("自动提交（无需人工确认）")
        upload_form.addRow("提交方式：", self._widgets["auto_submit"])
        self._widgets["max_title_length"] = QSpinBox()
        self._widgets["max_title_length"].setRange(10, 120)
        upload_form.addRow("标题最大长度：", self._widgets["max_title_length"])
        self._widgets["field_fill_delay_min"] = QDoubleSpinBox()
        self._widgets["field_fill_delay_min"].setRange(0.1, 5.0)
        self._widgets["field_fill_delay_min"].setSuffix(" 秒")
        upload_form.addRow("填写最小延迟：", self._widgets["field_fill_delay_min"])
        self._widgets["field_fill_delay_max"] = QDoubleSpinBox()
        self._widgets["field_fill_delay_max"].setRange(0.1, 5.0)
        self._widgets["field_fill_delay_max"].setSuffix(" 秒")
        upload_form.addRow("填写最大延迟：", self._widgets["field_fill_delay_max"])
        tabs.addTab(upload_tab, "上传")

        # 图片标签
        img_tab = QWidget()
        img_form = QFormLayout(img_tab)
        self._widgets["min_width"] = QSpinBox()
        self._widgets["min_width"].setRange(100, 2000)
        self._widgets["min_width"].setSuffix(" px")
        img_form.addRow("最小宽度：", self._widgets["min_width"])
        self._widgets["min_height"] = QSpinBox()
        self._widgets["min_height"].setRange(100, 2000)
        self._widgets["min_height"].setSuffix(" px")
        img_form.addRow("最小高度：", self._widgets["min_height"])
        self._widgets["max_main_images"] = QSpinBox()
        self._widgets["max_main_images"].setRange(1, 20)
        img_form.addRow("最大主图数：", self._widgets["max_main_images"])
        self._widgets["jpeg_quality"] = QSpinBox()
        self._widgets["jpeg_quality"].setRange(50, 100)
        self._widgets["jpeg_quality"].setSuffix(" %")
        img_form.addRow("JPEG质量：", self._widgets["jpeg_quality"])
        tabs.addTab(img_tab, "图片")

        layout.addWidget(tabs)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4285f4; color: white;
                border: none; border-radius: 6px;
                padding: 8px 28px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3367d6; }
        """)
        btn_save.clicked.connect(self._save_and_accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5; color: #666;
                border: 1px solid #ddd; border-radius: 6px;
                padding: 8px 28px; font-size: 14px;
            }
            QPushButton:hover { background-color: #e8e8e8; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _load_values(self):
        """从配置加载当前值"""
        mapping = {
            "headless": ("browser", "headless"),
            "slow_mo": ("browser", "slow_mo"),
            "api_wait_timeout": ("scraping", "api_wait_timeout"),
            "scroll_delay_min": ("scraping", "scroll_delay_min"),
            "scroll_delay_max": ("scraping", "scroll_delay_max"),
            "auto_submit": ("upload", "auto_submit"),
            "max_title_length": ("upload", "max_title_length"),
            "field_fill_delay_min": ("upload", "field_fill_delay_min"),
            "field_fill_delay_max": ("upload", "field_fill_delay_max"),
            "min_width": ("images", "min_width"),
            "min_height": ("images", "min_height"),
            "max_main_images": ("images", "max_main_images"),
            "jpeg_quality": ("images", "jpeg_quality"),
        }
        for widget_key, (section, key) in mapping.items():
            widget = self._widgets.get(widget_key)
            value = self._config.get(section, key)
            if value is None:
                continue
            if isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(value)

    def _save_and_accept(self):
        """保存配置并关闭"""
        mapping = {
            "headless": ("browser", "headless"),
            "slow_mo": ("browser", "slow_mo"),
            "api_wait_timeout": ("scraping", "api_wait_timeout"),
            "scroll_delay_min": ("scraping", "scroll_delay_min"),
            "scroll_delay_max": ("scraping", "scroll_delay_max"),
            "auto_submit": ("upload", "auto_submit"),
            "max_title_length": ("upload", "max_title_length"),
            "field_fill_delay_min": ("upload", "field_fill_delay_min"),
            "field_fill_delay_max": ("upload", "field_fill_delay_max"),
            "min_width": ("images", "min_width"),
            "min_height": ("images", "min_height"),
            "max_main_images": ("images", "max_main_images"),
            "jpeg_quality": ("images", "jpeg_quality"),
        }
        for widget_key, (section, key) in mapping.items():
            widget = self._widgets.get(widget_key)
            if isinstance(widget, QCheckBox):
                self._config.set(section, key, widget.isChecked())
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                self._config.set(section, key, widget.value())
        self.accept()
