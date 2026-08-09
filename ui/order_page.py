"""
订单管理页面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QMessageBox, QGroupBox, QHeaderView, QTextEdit
)
from PySide6.QtCore import Qt
from database import OrderDAO, ProductDAO


class OrderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_id = None
        self.setup_ui()
        self.load_products()
        self.load_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ---- 左侧表单 ----
        self.form_group = QGroupBox("记录订单")
        self.form_group.setObjectName("card")
        self.form_group.setFixedWidth(360)
        form_layout = QVBoxLayout(self.form_group)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(20, 24, 20, 24)

        lbl = QLabel("选择商品")
        lbl.setObjectName("formLabel")
        form_layout.addWidget(lbl)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(38)
        form_layout.addWidget(self.product_combo)

        # 成本提示
        self.cost_hint = QLabel("成本：¥0.00")
        self.cost_hint.setObjectName("hintLabel")
        form_layout.addWidget(self.cost_hint)
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)

        lbl2 = QLabel("售价 (元)")
        lbl2.setObjectName("formLabel")
        form_layout.addWidget(lbl2)

        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setRange(0, 9999999)
        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setPrefix("¥ ")
        self.sale_price_input.setMinimumHeight(38)
        self.sale_price_input.valueChanged.connect(self.calc_profit)
        form_layout.addWidget(self.sale_price_input)

        lbl3 = QLabel("数量")
        lbl3.setObjectName("formLabel")
        form_layout.addWidget(lbl3)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 99999)
        self.quantity_input.setValue(1)
        self.quantity_input.setMinimumHeight(38)
        self.quantity_input.valueChanged.connect(self.calc_profit)
        form_layout.addWidget(self.quantity_input)

        lbl4 = QLabel("预估利润")
        lbl4.setObjectName("formLabel")
        form_layout.addWidget(lbl4)

        self.profit_display = QLabel("¥0.00")
        self.profit_display.setObjectName("profitBig")
        form_layout.addWidget(self.profit_display)

        lbl5 = QLabel("备注")
        lbl5.setObjectName("formLabel")
        form_layout.addWidget(lbl5)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("订单备注（选填）")
        self.notes_input.setMaximumHeight(100)
        form_layout.addWidget(self.notes_input)

        form_layout.addSpacing(8)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("＋ 记录订单")
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.setMinimumHeight(44)
        self.add_btn.clicked.connect(self.save_order)
        btn_row.addWidget(self.add_btn)

        self.cancel_btn = QPushButton("取消编辑")
        self.cancel_btn.setMinimumHeight(44)
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setVisible(False)
        btn_row.addWidget(self.cancel_btn)

        form_layout.addLayout(btn_row)
        form_layout.addStretch()
        main_layout.addWidget(self.form_group)

        # ---- 右侧表格 ----
        right_group = QGroupBox("订单列表")
        right_group.setObjectName("card")
        right_layout = QVBoxLayout(right_group)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(20, 24, 20, 24)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "商品", "供货商", "成本", "售价", "数量", "利润", "销售额", "备注", "时间"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 45)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumWidth(650)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.edit_order)
        right_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.edit_btn = QPushButton("编辑选中")
        self.edit_btn.setMinimumHeight(36)
        self.edit_btn.setMinimumWidth(100)
        self.edit_btn.clicked.connect(self.edit_order)
        btn_layout.addWidget(self.edit_btn)

        self.del_btn = QPushButton("删除选中")
        self.del_btn.setObjectName("dangerBtn")
        self.del_btn.setMinimumHeight(36)
        self.del_btn.setMinimumWidth(100)
        self.del_btn.clicked.connect(self.delete_order)
        btn_layout.addWidget(self.del_btn)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(right_group, 1)

    def load_products(self):
        self.product_combo.clear()
        products = ProductDAO.get_all()
        self.product_data = {p["id"]: p for p in products}
        for p in products:
            cost = p["purchase_price"] + p["shipping_cost"]
            self.product_combo.addItem(
                f"[{p.get('supplier_name', '')}] {p['name']} (成本¥{cost:.2f})",
                p["id"]
            )
        self.on_product_changed()

    def on_product_changed(self):
        pid = self.product_combo.currentData()
        if pid and pid in self.product_data:
            p = self.product_data[pid]
            cost = p["purchase_price"] + p["shipping_cost"]
            self.cost_hint.setText(f"成本：¥{cost:.2f} （拿货价 ¥{p['purchase_price']:.2f} + 运费 ¥{p['shipping_cost']:.2f}）")
        self.calc_profit()

    def calc_profit(self):
        pid = self.product_combo.currentData()
        if pid and pid in self.product_data:
            p = self.product_data[pid]
            cost = p["purchase_price"] + p["shipping_cost"]
            qty = self.quantity_input.value()
            sale = self.sale_price_input.value()
            profit = (sale - cost) * qty
            self.profit_display.setText(f"¥{profit:.2f}")
            if profit > 0:
                self.profit_display.setStyleSheet("color: #27ae60; font-size: 22px; font-weight: bold;")
            elif profit < 0:
                self.profit_display.setStyleSheet("color: #e74c3c; font-size: 22px; font-weight: bold;")
            else:
                self.profit_display.setStyleSheet("color: #7f8c8d; font-size: 22px; font-weight: bold;")

    def load_data(self):
        orders = OrderDAO.get_all()
        self.table.setRowCount(len(orders))
        for row, o in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(o["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(o.get("product_name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(o.get("supplier_name", "")))
            cost = (o.get("purchase_price", 0) or 0) + (o.get("shipping_cost", 0) or 0)
            self.table.setItem(row, 3, QTableWidgetItem(f"¥{cost:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"¥{o['sale_price']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(o["quantity"])))
            profit = o["profit"]
            p_item = QTableWidgetItem(f"¥{profit:.2f}")
            if profit > 0:
                p_item.setForeground(Qt.darkGreen)
            elif profit < 0:
                p_item.setForeground(Qt.red)
            self.table.setItem(row, 6, p_item)
            sales = o["sale_price"] * o["quantity"]
            self.table.setItem(row, 7, QTableWidgetItem(f"¥{sales:.2f}"))
            self.table.setItem(row, 8, QTableWidgetItem(o.get("notes", "")))
            self.table.setItem(row, 9, QTableWidgetItem(o.get("created_at", "")))

    def _clear_form(self):
        self.sale_price_input.setValue(0)
        self.quantity_input.setValue(1)
        self.notes_input.clear()
        if self.product_combo.count() > 0:
            self.product_combo.setCurrentIndex(0)

    def _enter_edit_mode(self):
        self.form_group.setTitle("编辑订单")
        self.add_btn.setText("💾 保存修改")
        self.add_btn.setStyleSheet(
            "QPushButton{background-color:#f59e0b;color:#fff;border:none;border-radius:8px;"
            "padding:12px 20px;font-size:14px;font-weight:600;}"
            "QPushButton:hover{background-color:#d97706;}"
        )
        self.cancel_btn.setVisible(True)

    def _exit_edit_mode(self):
        self.editing_id = None
        self.form_group.setTitle("记录订单")
        self.add_btn.setText("＋ 记录订单")
        self.add_btn.setStyleSheet("")
        self.cancel_btn.setVisible(False)
        self._clear_form()

    def edit_order(self):
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "提示", "请先选中要编辑的订单或双击行")
            return
        row = self.table.currentRow()
        oid = int(self.table.item(row, 0).text())
        sale_text = self.table.item(row, 4).text().replace("¥", "").strip()
        qty = int(self.table.item(row, 5).text())
        notes = self.table.item(row, 8).text() if self.table.item(row, 8) else ""

        # 匹配商品 (通过商品名)
        product_name = self.table.item(row, 1).text()
        matched = False
        for i in range(self.product_combo.count()):
            if product_name in self.product_combo.itemText(i):
                self.product_combo.setCurrentIndex(i)
                matched = True
                break
        if not matched and self.product_combo.count() > 0:
            self.product_combo.setCurrentIndex(0)

        self.editing_id = oid
        self._enter_edit_mode()
        self.sale_price_input.setValue(float(sale_text))
        self.quantity_input.setValue(qty)
        self.notes_input.setPlainText(notes)

    def cancel_edit(self):
        self._exit_edit_mode()

    def save_order(self):
        pid = self.product_combo.currentData()
        if not pid:
            QMessageBox.warning(self, "提示", "请先添加商品")
            return
        sale_price = self.sale_price_input.value()
        quantity = self.quantity_input.value()
        notes = self.notes_input.toPlainText().strip()

        p = self.product_data[pid]
        cost = p["purchase_price"] + p["shipping_cost"]
        profit = (sale_price - cost) * quantity

        if self.editing_id is not None:
            OrderDAO.update(self.editing_id, pid, sale_price, quantity, profit, notes)
            self._exit_edit_mode()
        else:
            OrderDAO.add(pid, sale_price, quantity, profit, notes)
            self._clear_form()
        self.load_data()

    def delete_order(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选中要删除的订单")
            return
        oid = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除订单 #{oid}？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.editing_id == oid:
                self._exit_edit_mode()
            OrderDAO.delete(oid)
            self.load_data()
