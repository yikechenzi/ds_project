"""
商品管理页面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QMessageBox, QGroupBox, QHeaderView, QGridLayout
)
from PySide6.QtCore import Qt
from database import ProductDAO, SupplierDAO


class ProductPage(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_id = None
        self.setup_ui()
        self.load_suppliers()
        self.load_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ---- 左侧表单 ----
        self.form_group = QGroupBox("添加商品")
        self.form_group.setObjectName("card")
        self.form_group.setFixedWidth(360)
        form_layout = QVBoxLayout(self.form_group)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(20, 24, 20, 24)

        lbl = QLabel("选择供货商")
        lbl.setObjectName("formLabel")
        form_layout.addWidget(lbl)

        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumHeight(38)
        form_layout.addWidget(self.supplier_combo)

        lbl2 = QLabel("商品名称")
        lbl2.setObjectName("formLabel")
        form_layout.addWidget(lbl2)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入商品名称")
        self.name_input.setMinimumHeight(38)
        form_layout.addWidget(self.name_input)

        lbl3 = QLabel("拿货价格 (元)")
        lbl3.setObjectName("formLabel")
        form_layout.addWidget(lbl3)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 9999999)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("¥ ")
        self.price_input.setMinimumHeight(38)
        form_layout.addWidget(self.price_input)

        lbl4 = QLabel("运费 (元)")
        lbl4.setObjectName("formLabel")
        form_layout.addWidget(lbl4)

        self.shipping_input = QDoubleSpinBox()
        self.shipping_input.setRange(0, 9999999)
        self.shipping_input.setDecimals(2)
        self.shipping_input.setPrefix("¥ ")
        self.shipping_input.setMinimumHeight(38)
        form_layout.addWidget(self.shipping_input)

        lbl5 = QLabel("商品链接")
        lbl5.setObjectName("formLabel")
        form_layout.addWidget(lbl5)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("请输入商品链接（选填）")
        self.link_input.setMinimumHeight(38)
        form_layout.addWidget(self.link_input)

        form_layout.addSpacing(8)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("＋ 添加商品")
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.setMinimumHeight(44)
        self.add_btn.clicked.connect(self.save_product)
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
        right_group = QGroupBox("商品列表")
        right_group.setObjectName("card")
        right_layout = QVBoxLayout(right_group)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(20, 24, 20, 24)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "供货商", "商品名称", "拿货价", "运费", "成本合计", "链接"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumWidth(600)
        self.table.doubleClicked.connect(self.edit_product)
        right_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setMinimumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_all)
        btn_layout.addWidget(self.refresh_btn)

        self.edit_btn = QPushButton("编辑选中")
        self.edit_btn.setMinimumHeight(36)
        self.edit_btn.setMinimumWidth(100)
        self.edit_btn.clicked.connect(self.edit_product)
        btn_layout.addWidget(self.edit_btn)

        self.del_btn = QPushButton("删除选中")
        self.del_btn.setObjectName("dangerBtn")
        self.del_btn.setMinimumHeight(36)
        self.del_btn.setMinimumWidth(100)
        self.del_btn.clicked.connect(self.delete_product)
        btn_layout.addWidget(self.del_btn)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(right_group, 1)

    def load_suppliers(self):
        self.supplier_combo.clear()
        suppliers = SupplierDAO.get_all()
        self.supplier_data = suppliers
        for s in suppliers:
            self.supplier_combo.addItem(f"[{s['type']}] {s['name']}", s["id"])

    def load_data(self):
        products = ProductDAO.get_all()
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(p.get("supplier_name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"¥{p['purchase_price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"¥{p['shipping_cost']:.2f}"))
            total = p["purchase_price"] + p["shipping_cost"]
            self.table.setItem(row, 5, QTableWidgetItem(f"¥{total:.2f}"))
            link = p.get("link", "")
            item = QTableWidgetItem(link if link else "-")
            if link:
                item.setForeground(Qt.blue)
            self.table.setItem(row, 6, item)

    def _clear_form(self):
        self.name_input.clear()
        self.price_input.setValue(0)
        self.shipping_input.setValue(0)
        self.link_input.clear()
        if self.supplier_combo.count() > 0:
            self.supplier_combo.setCurrentIndex(0)

    def _enter_edit_mode(self):
        self.form_group.setTitle("编辑商品")
        self.add_btn.setText("💾 保存修改")
        self.add_btn.setStyleSheet(
            "QPushButton{background-color:#f59e0b;color:#fff;border:none;border-radius:8px;"
            "padding:12px 20px;font-size:14px;font-weight:600;}"
            "QPushButton:hover{background-color:#d97706;}"
        )
        self.cancel_btn.setVisible(True)

    def _exit_edit_mode(self):
        self.editing_id = None
        self.form_group.setTitle("添加商品")
        self.add_btn.setText("＋ 添加商品")
        self.add_btn.setStyleSheet("")
        self.cancel_btn.setVisible(False)
        self._clear_form()

    def edit_product(self):
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "提示", "请先选中要编辑的商品或双击行")
            return
        row = self.table.currentRow()
        pid = int(self.table.item(row, 0).text())
        supplier_name = self.table.item(row, 1).text()
        name = self.table.item(row, 2).text()
        price_text = self.table.item(row, 3).text().replace("¥", "").strip()
        shipping_text = self.table.item(row, 4).text().replace("¥", "").strip()
        link = self.table.item(row, 6).text()
        link = "" if link == "-" else link

        # 匹配供货商
        for i in range(self.supplier_combo.count()):
            if self.supplier_combo.itemText(i).endswith(supplier_name):
                self.supplier_combo.setCurrentIndex(i)
                break

        self.editing_id = pid
        self._enter_edit_mode()
        self.name_input.setText(name)
        self.price_input.setValue(float(price_text))
        self.shipping_input.setValue(float(shipping_text))
        self.link_input.setText(link)

    def cancel_edit(self):
        self._exit_edit_mode()

    def save_product(self):
        if not self.supplier_data:
            QMessageBox.warning(self, "提示", "请先在供货商页面添加供货商")
            return
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入商品名称")
            return
        sid = self.supplier_combo.currentData()
        price = self.price_input.value()
        shipping = self.shipping_input.value()
        link = self.link_input.text().strip()

        if self.editing_id is not None:
            ProductDAO.update(self.editing_id, sid, name, price, shipping, link)
            self._exit_edit_mode()
        else:
            ProductDAO.add(sid, name, price, shipping, link)
            self._clear_form()
        self.load_data()

    def delete_product(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选中要删除的商品")
            return
        pid = int(self.table.item(row, 0).text())
        name = self.table.item(row, 2).text()
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除商品「{name}」？\n其关联的订单也会一并删除。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.editing_id == pid:
                self._exit_edit_mode()
            ProductDAO.delete(pid)
            self.load_data()

    def refresh_all(self):
        self.load_suppliers()
        self.load_data()
