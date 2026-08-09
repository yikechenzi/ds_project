"""
首页 - 数据概览仪表盘
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from database import SupplierDAO, ProductDAO, OrderDAO


class StatCard(QFrame):
    """数据卡片组件"""
    def __init__(self, title, value, color, icon_text):
        super().__init__()
        self.setObjectName("statCard")
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        top = QHBoxLayout()
        icon = QLabel(icon_text)
        icon.setStyleSheet(f"font-size: 28px; background: transparent;")
        top.addWidget(icon)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("statTitle")
        title_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px; background: transparent;")
        top.addWidget(title_lbl)
        top.addStretch()
        layout.addLayout(top)

        value_lbl = QLabel(str(value))
        value_lbl.setObjectName("statValue")
        value_lbl.setStyleSheet(
            f"color: {color}; font-size: 32px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(value_lbl)
        layout.addStretch()


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # 每5秒自动刷新

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(28, 28, 28, 28)

        # ---- 欢迎标题 ----
        title = QLabel("📊 数据概览")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        subtitle = QLabel("实时了解您的电商选品经营状况")
        subtitle.setStyleSheet("font-size: 13px; color: #95a5a6; margin-bottom: 4px;")
        main_layout.addWidget(subtitle)

        # ---- 统计卡片 ----
        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        self.card_orders = StatCard("总订单数", "0", "#3498db", "📦")
        self.card_sales = StatCard("总销售额", "¥0", "#9b59b6", "💰")
        self.card_profit = StatCard("总利润", "¥0", "#27ae60", "📈")
        self.card_today = StatCard("今日利润", "¥0", "#e67e22", "🔥")

        cards_layout.addWidget(self.card_orders, 0, 0)
        cards_layout.addWidget(self.card_sales, 0, 1)
        cards_layout.addWidget(self.card_profit, 0, 2)
        cards_layout.addWidget(self.card_today, 0, 3)

        main_layout.addLayout(cards_layout)

        # 次要指标
        sub_cards = QHBoxLayout()
        sub_cards.setSpacing(16)
        self.supplier_count = StatCard("供货商数", "0", "#1abc9c", "🏭")
        self.product_count = StatCard("商品数", "0", "#3498db", "🛍️")
        sub_cards.addWidget(self.supplier_count)
        sub_cards.addWidget(self.product_count)
        main_layout.addLayout(sub_cards)

        # ---- 最近订单表格 ----
        table_group = QGroupBox("最近订单")
        table_group.setObjectName("card")
        table_layout = QVBoxLayout(table_group)
        table_layout.setSpacing(10)
        table_layout.setContentsMargins(16, 12, 16, 12)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(7)
        self.order_table.setHorizontalHeaderLabels([
            "时间", "商品", "供货商", "售价", "数量", "利润", "备注"
        ])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setAlternatingRowColors(True)
        self.order_table.setMaximumHeight(260)
        table_layout.addWidget(self.order_table)

        main_layout.addWidget(table_group, 1)

    def refresh_data(self):
        stats = OrderDAO.get_stats()
        s_count = SupplierDAO.count()
        p_count = ProductDAO.count()

        # 更新卡片 - 重新创建 StatCard 以更新值
        self._update_card(self.card_orders, "总订单数", str(stats["total_orders"]), "#3498db", "📦")
        self._update_card(self.card_sales, "总销售额", f"¥{stats['total_sales']:,.2f}", "#9b59b6", "💰")
        self._update_card(self.card_profit, "总利润", f"¥{stats['total_profit']:,.2f}", "#27ae60", "📈")
        self._update_card(self.card_today, "今日利润", f"¥{stats['today_profit']:,.2f}", "#e67e22", "🔥")
        self._update_card(self.supplier_count, "供货商数", str(s_count), "#1abc9c", "🏭")
        self._update_card(self.product_count, "商品数", str(p_count), "#3498db", "🛍️")

        # 最近订单
        orders = OrderDAO.get_all()
        recent = orders[:20]
        self.order_table.setRowCount(len(recent))
        for row, o in enumerate(recent):
            self.order_table.setItem(row, 0, QTableWidgetItem(o.get("created_at", "")))
            self.order_table.setItem(row, 1, QTableWidgetItem(o.get("product_name", "")))
            self.order_table.setItem(row, 2, QTableWidgetItem(o.get("supplier_name", "")))
            self.order_table.setItem(row, 3, QTableWidgetItem(f"¥{o['sale_price']:.2f}"))
            self.order_table.setItem(row, 4, QTableWidgetItem(str(o["quantity"])))
            p = o["profit"]
            pi = QTableWidgetItem(f"¥{p:.2f}")
            if p > 0:
                pi.setForeground(Qt.darkGreen)
            elif p < 0:
                pi.setForeground(Qt.red)
            self.order_table.setItem(row, 5, pi)
            self.order_table.setItem(row, 6, QTableWidgetItem(o.get("notes", "")))

    def _update_card(self, card_widget, title, value, color, icon):
        """更新卡片内容"""
        layout = card_widget.layout()
        # 清除旧内容
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        top.addWidget(icon_lbl)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("statTitle")
        title_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px; background: transparent;")
        top.addWidget(title_lbl)
        top.addStretch()
        layout.addLayout(top)

        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet(
            f"color: {color}; font-size: 32px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(value_lbl)
        layout.addStretch()
