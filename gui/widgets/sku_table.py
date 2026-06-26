"""
SKU编辑表格组件
支持SKU规格的查看、编辑和批量修改
"""
from PySide6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QHBoxLayout, QPushButton, QHeaderView, QDoubleSpinBox,
    QSpinBox, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal


class SkuTable(QWidget):
    """SKU规格编辑表格"""

    data_changed = Signal()

    HEADERS = ["规格名称", "价格", "库存", "SKU编码"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 批量操作栏
        toolbar = QHBoxLayout()
        self._btn_set_price = QPushButton("批量设置价格")
        self._btn_set_stock = QPushButton("批量设置库存")
        self._btn_set_price.clicked.connect(self._batch_set_price)
        self._btn_set_stock.clicked.connect(self._batch_set_stock)
        toolbar.addWidget(self._btn_set_price)
        toolbar.addWidget(self._btn_set_stock)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 表格
        self._table = QTableWidget(0, len(self.HEADERS))
        self._table.setHorizontalHeaderLabels(self.HEADERS)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self._table.itemChanged.connect(lambda: self.data_changed.emit())
        layout.addWidget(self._table)

    def set_data(self, sku_list: list):
        """加载SKU数据"""
        self._table.blockSignals(True)
        self._table.setRowCount(len(sku_list))
        for row, sku in enumerate(sku_list):
            # 规格名称（只读）
            name_item = QTableWidgetItem(sku.get("name", ""))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 0, name_item)

            # 价格
            price_spin = QDoubleSpinBox()
            price_spin.setRange(0, 999999)
            price_spin.setDecimals(2)
            price_spin.setPrefix("¥")
            price_spin.setValue(sku.get("price", 0))
            self._table.setCellWidget(row, 1, price_spin)

            # 库存
            stock_spin = QSpinBox()
            stock_spin.setRange(0, 999999)
            stock_spin.setValue(sku.get("stock", 100))
            self._table.setCellWidget(row, 2, stock_spin)

            # 编码（只读）
            code_item = QTableWidgetItem(sku.get("sku_code", ""))
            code_item.setFlags(code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 3, code_item)
        self._table.blockSignals(False)

    def get_data(self) -> list:
        """获取编辑后的SKU数据"""
        result = []
        for row in range(self._table.rowCount()):
            price_spin = self._table.cellWidget(row, 1)
            stock_spin = self._table.cellWidget(row, 2)
            result.append({
                "name": self._table.item(row, 0).text() if self._table.item(row, 0) else "",
                "price": price_spin.value() if price_spin else 0,
                "stock": stock_spin.value() if stock_spin else 100,
                "sku_code": self._table.item(row, 3).text() if self._table.item(row, 3) else "",
            })
        return result

    def _batch_set_price(self):
        """批量设置价格"""
        rows = set(idx.row() for idx in self._table.selectedIndexes())
        if not rows:
            rows = range(self._table.rowCount())
        # 使用第一行的价格
        if rows:
            first_price = self._table.cellWidget(list(rows)[0] if isinstance(rows, set) else rows[0], 1)
            val = first_price.value() if first_price else 0
            for row in rows:
                spin = self._table.cellWidget(row, 1)
                if spin:
                    spin.setValue(val)

    def _batch_set_stock(self):
        """批量设置库存"""
        rows = set(idx.row() for idx in self._table.selectedIndexes())
        if not rows:
            rows = range(self._table.rowCount())
        for row in rows:
            spin = self._table.cellWidget(row, 2)
            if spin:
                spin.setValue(100)

    def clear(self):
        """清空表格"""
        self._table.setRowCount(0)
