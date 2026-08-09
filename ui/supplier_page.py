"""
供货商管理页面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QHeaderView,
    QMessageBox, QGroupBox, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from database import SupplierDAO


class SupplierPage(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_id = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ---- 左侧表单 ----
        self.form_group = QGroupBox("添加供货商")
        self.form_group.setObjectName("card")
        self.form_group.setFixedWidth(360)
        form_layout = QVBoxLayout(self.form_group)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(20, 24, 20, 24)

        lbl = QLabel("供货商类型")
        lbl.setObjectName("formLabel")
        form_layout.addWidget(lbl)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["线上", "线下"])
        self.type_combo.setMinimumHeight(38)
        form_layout.addWidget(self.type_combo)

        lbl2 = QLabel("供货商名称")
        lbl2.setObjectName("formLabel")
        form_layout.addWidget(lbl2)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入供货商名称")
        self.name_input.setMinimumHeight(38)
        form_layout.addWidget(self.name_input)

        lbl3 = QLabel("备注")
        lbl3.setObjectName("formLabel")
        form_layout.addWidget(lbl3)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注信息（选填）")
        self.notes_input.setMaximumHeight(120)
        form_layout.addWidget(self.notes_input)

        form_layout.addSpacing(8)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("＋ 添加供货商")
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.setMinimumHeight(44)
        self.add_btn.clicked.connect(self.save_supplier)
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
        right_group = QGroupBox("供货商列表")
        right_group.setObjectName("card")
        right_layout = QVBoxLayout(right_group)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(20, 24, 20, 24)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "名称", "类型", "备注"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumWidth(520)
        self.table.doubleClicked.connect(self.edit_supplier)
        right_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.edit_btn = QPushButton("编辑选中")
        self.edit_btn.setMinimumHeight(36)
        self.edit_btn.setMinimumWidth(100)
        self.edit_btn.clicked.connect(self.edit_supplier)
        btn_layout.addWidget(self.edit_btn)

        self.del_btn = QPushButton("删除选中")
        self.del_btn.setObjectName("dangerBtn")
        self.del_btn.setMinimumHeight(36)
        self.del_btn.setMinimumWidth(100)
        self.del_btn.clicked.connect(self.delete_supplier)
        btn_layout.addWidget(self.del_btn)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(right_group, 1)

    def load_data(self):
        suppliers = SupplierDAO.get_all()
        self.table.setRowCount(len(suppliers))
        for row, s in enumerate(suppliers):
            self.table.setItem(row, 0, QTableWidgetItem(str(s["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(s["name"]))
            type_item = QTableWidgetItem(s["type"])
            if s["type"] == "线上":
                type_item.setForeground(Qt.blue)
            else:
                type_item.setForeground(QColor("#e67e22"))
            self.table.setItem(row, 2, type_item)
            self.table.setItem(row, 3, QTableWidgetItem(s.get("notes", "")))

    def _clear_form(self):
        self.name_input.clear()
        self.notes_input.clear()
        self.type_combo.setCurrentIndex(0)

    def _enter_edit_mode(self):
        self.form_group.setTitle("编辑供货商")
        self.add_btn.setText("💾 保存修改")
        self.add_btn.setStyleSheet(
            "QPushButton{background-color:#f59e0b;color:#fff;border:none;border-radius:8px;"
            "padding:12px 20px;font-size:14px;font-weight:600;}"
            "QPushButton:hover{background-color:#d97706;}"
        )
        self.cancel_btn.setVisible(True)

    def _exit_edit_mode(self):
        self.editing_id = None
        self.form_group.setTitle("添加供货商")
        self.add_btn.setText("＋ 添加供货商")
        self.add_btn.setStyleSheet("")
        self.cancel_btn.setVisible(False)
        self._clear_form()

    def edit_supplier(self):
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "提示", "请先选中要编辑的供货商或双击行")
            return
        row = self.table.currentRow()
        sid = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        stype = self.table.item(row, 2).text()
        notes = self.table.item(row, 3).text() if self.table.item(row, 3) else ""

        self.editing_id = sid
        self._enter_edit_mode()
        self.name_input.setText(name)
        self.type_combo.setCurrentText(stype)
        self.notes_input.setPlainText(notes)

    def cancel_edit(self):
        self._exit_edit_mode()

    def save_supplier(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入供货商名称")
            return
        stype = self.type_combo.currentText()
        notes = self.notes_input.toPlainText().strip()

        if self.editing_id is not None:
            SupplierDAO.update(self.editing_id, name, stype, notes)
            self._exit_edit_mode()
        else:
            SupplierDAO.add(name, stype, notes)
            self._clear_form()
        self.load_data()

    def delete_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选中要删除的供货商")
            return
        sid = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除供货商「{name}」？\n其关联的商品也会一并删除。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.editing_id == sid:
                self._exit_edit_mode()
            SupplierDAO.delete(sid)
            self.load_data()
