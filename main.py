"""
电商选品软件 - 主入口
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from database import init_db
from ui.home_page import HomePage
from ui.supplier_page import SupplierPage
from ui.product_page import ProductPage
from ui.order_page import OrderPage


STYLE_QSS = """
/* ========== 全局样式 ========== */
QMainWindow {
    background-color: #f0f2f5;
}

QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* ========== 左侧导航栏 ========== */
#navBar {
    background-color: #1e293b;
    border-right: none;
}

#navTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    padding: 16px;
    background: transparent;
}

#navSubtitle {
    color: #94a3b8;
    font-size: 11px;
    padding: 0 16px 8px 16px;
    background: transparent;
}

/* 导航按钮 */
.NavButton {
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    margin: 2px 10px;
}

.NavButton:hover {
    background-color: #334155;
    color: #f1f5f9;
}

.NavButton:checked, .NavButton[active="true"] {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

/* ========== 通用卡片 ========== */
#card {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

QGroupBox#card {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    font-weight: bold;
    font-size: 15px;
    color: #1e293b;
    padding-top: 10px;
}

QGroupBox#card::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}

/* ========== 统计卡片 ========== */
#statCard {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

#statTitle {
    color: #94a3b8;
    font-size: 13px;
    background: transparent;
}

#statValue {
    font-size: 32px;
    font-weight: bold;
    background: transparent;
}

/* ========== 表单标签 ========== */
#formLabel {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    margin-bottom: 2px;
}

/* ========== 提示标签 ========== */
#hintLabel {
    font-size: 12px;
    color: #64748b;
    padding: 4px 0;
}

#profitBig {
    font-size: 22px;
    font-weight: bold;
    color: #27ae60;
    padding: 4px 0;
}

/* ========== 输入框 ========== */
QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox {
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #f8fafc;
    color: #1e293b;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border-color: #3b82f6;
    background-color: #ffffff;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    selection-background-color: #eff6ff;
    selection-color: #1e293b;
    padding: 4px;
}

/* ========== 按钮样式 ========== */
QPushButton {
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    border: none;
}

#primaryBtn {
    background-color: #3b82f6;
    color: #ffffff;
}

#primaryBtn:hover {
    background-color: #2563eb;
}

#primaryBtn:pressed {
    background-color: #1d4ed8;
}

#dangerBtn {
    background-color: #fef2f2;
    color: #ef4444;
    border: 1px solid #fecaca;
}

#dangerBtn:hover {
    background-color: #fee2e2;
    color: #dc2626;
}

/* 普通按钮 */
QPushButton:!primaryBtn:!dangerBtn {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
}

QPushButton:!primaryBtn:!dangerBtn:hover {
    background-color: #e2e8f0;
}

/* ========== 表格样式 ========== */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    selection-background-color: #eff6ff;
    selection-color: #1e293b;
    outline: none;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f8fafc;
}

QTableWidget::item:alternate {
    background-color: #fafbfc;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #1e293b;
}

/* ========== 滚动条 ========== */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ========== 提示框 ========== */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1e293b;
    font-size: 14px;
}
"""


class NavButton(QPushButton):
    """自定义导航按钮"""
    def __init__(self, text, icon=""):
        super().__init__(f"  {icon}  {text}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(46)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电商选品管理系统")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 680)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ====== 左侧导航栏 ======
        nav = QFrame()
        nav.setObjectName("navBar")
        nav.setFixedWidth(220)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # Logo 区域
        logo_area = QFrame()
        logo_area.setStyleSheet("background-color: #0f172a; padding: 8px 0;")
        logo_layout = QVBoxLayout(logo_area)
        logo_layout.setContentsMargins(16, 18, 16, 14)

        title = QLabel("🛒 选品助手")
        title.setObjectName("navTitle")
        logo_layout.addWidget(title)

        sub = QLabel("电商选品管理系统 v1.0")
        sub.setObjectName("navSubtitle")
        logo_layout.addWidget(sub)
        nav_layout.addWidget(logo_area)

        # 分割线
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #334155; max-height: 1px; margin: 0;")
        nav_layout.addWidget(sep)

        nav_layout.addSpacing(12)

        # 导航按钮
        self.btn_home = NavButton("首页", "🏠")
        self.btn_supplier = NavButton("供货商", "🏭")
        self.btn_product = NavButton("商品管理", "📦")
        self.btn_order = NavButton("订单管理", "📋")

        self.nav_buttons = [self.btn_home, self.btn_supplier, self.btn_product, self.btn_order]

        for btn in self.nav_buttons:
            btn.clicked.connect(self._make_switch_handler(btn))
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

        # 底部作者信息
        footer = QLabel("© 2026 选品助手")
        footer.setStyleSheet("color: #64748b; font-size: 12px; padding: 16px; background: transparent;")
        footer.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(footer)

        main_layout.addWidget(nav)

        # ====== 右侧内容区 ======
        self.stack = QStackedWidget()
        self.page_home = HomePage()
        self.page_supplier = SupplierPage()
        self.page_product = ProductPage()
        self.page_order = OrderPage()

        self.stack.addWidget(self.page_home)       # 0
        self.stack.addWidget(self.page_supplier)   # 1
        self.stack.addWidget(self.page_product)    # 2
        self.stack.addWidget(self.page_order)      # 3

        main_layout.addWidget(self.stack, 1)

        # 默认选中首页
        self.btn_home.setChecked(True)
        self._update_nav_style(self.btn_home)

    def _make_switch_handler(self, btn):
        """为导航按钮创建切换回调"""
        btn_map = {
            self.btn_home: 0,
            self.btn_supplier: 1,
            self.btn_product: 2,
            self.btn_order: 3,
        }
        index = btn_map.get(btn, 0)

        def handler():
            # 离开当前页时取消编辑状态
            self.page_supplier.cancel_edit()
            self.page_product.cancel_edit()
            self.page_order.cancel_edit()

            # 刷新对应页面数据
            if index == 0:
                self.page_home.refresh_data()
            elif index == 1:
                self.page_supplier.load_data()
            elif index == 2:
                self.page_product.refresh_all()
            elif index == 3:
                self.page_order.load_data()
                self.page_order.load_products()

            self.stack.setCurrentIndex(index)
            for b in self.nav_buttons:
                b.setChecked(b is btn)
                self._update_nav_style(b)
        return handler

    def _update_nav_style(self, btn):
        if btn.isChecked():
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    margin: 2px 10px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #cbd5e1;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 12px 20px;
                    font-size: 14px;
                    margin: 2px 10px;
                }
                QPushButton:hover {
                    background-color: #334155;
                    color: #f1f5f9;
                }
            """)

    def apply_styles(self):
        self.setStyleSheet(STYLE_QSS)


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 设置默认字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
