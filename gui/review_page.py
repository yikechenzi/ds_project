"""
审核页面
展示采集到的商品信息，支持编辑后确认上架
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QSplitter, QScrollArea, QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from gui.widgets.image_preview import ImagePreview
from gui.widgets.sku_table import SkuTable
from gui.widgets.attribute_form import AttributeForm
from gui.widgets.log_console import LogConsole
from models.product import Product


class ReviewPage(QWidget):
    """审核页面：预览并编辑商品信息"""

    confirm_clicked = Signal(object)  # Product
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._product: Product | None = None
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # 标题
        header = QLabel("📋 商品审核")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        main_layout.addWidget(header)

        # 使用分割器左右布局
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---- 左侧：编辑区 ----
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)

        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("商品标题")
        self._title_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ddd; border-radius: 4px;")
        info_layout.addWidget(QLabel("标题："))
        info_layout.addWidget(self._title_input)

        self._price_input = QLineEdit()
        self._price_input.setPlaceholderText("价格")
        self._price_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ddd; border-radius: 4px;")
        info_layout.addWidget(QLabel("价格（¥）："))
        info_layout.addWidget(self._price_input)
        left_layout.addWidget(info_group)

        # SKU表格
        sku_group = QGroupBox("SKU 规格")
        sku_layout = QVBoxLayout(sku_group)
        self._sku_table = SkuTable()
        sku_layout.addWidget(self._sku_table)
        left_layout.addWidget(sku_group)

        # 属性表单
        attr_group = QGroupBox("商品属性")
        attr_layout = QVBoxLayout(attr_group)
        self._attr_form = AttributeForm()
        attr_layout.addWidget(self._attr_form)
        left_layout.addWidget(attr_group)

        # 按钮区
        btn_layout = QHBoxLayout()
        self._btn_back = QPushButton("← 返回采集")
        self._btn_back.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5; color: #666;
                border: 1px solid #ddd; border-radius: 6px;
                padding: 10px 20px; font-size: 13px;
            }
            QPushButton:hover { background-color: #e8e8e8; }
        """)
        self._btn_back.clicked.connect(self.back_clicked.emit)

        self._btn_confirm = QPushButton("确认上架 →")
        self._btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #3cb44b; color: white;
                border: none; border-radius: 6px;
                padding: 10px 28px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2d963a; }
        """)
        self._btn_confirm.clicked.connect(self._on_confirm)

        btn_layout.addWidget(self._btn_back)
        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_confirm)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left_widget)

        # ---- 右侧：预览区 ----
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 0, 0, 0)

        preview_group = QGroupBox("图片预览")
        preview_layout = QVBoxLayout(preview_group)
        self._image_preview = ImagePreview()
        preview_layout.addWidget(self._image_preview)
        right_layout.addWidget(preview_group)

        # 店铺信息
        shop_group = QGroupBox("店铺信息")
        shop_layout = QVBoxLayout(shop_group)
        self._shop_label = QLabel("店铺：-")
        self._shop_label.setStyleSheet("font-size: 13px; color: #666;")
        shop_layout.addWidget(self._shop_label)
        self._source_label = QLabel("来源：-")
        self._source_label.setStyleSheet("font-size: 12px; color: #999;")
        self._source_label.setWordWrap(True)
        shop_layout.addWidget(self._source_label)
        right_layout.addWidget(shop_group)

        right_layout.addStretch()
        splitter.addWidget(right_widget)
        splitter.setSizes([550, 350])

        main_layout.addWidget(splitter, stretch=1)

    def set_product(self, product: Product):
        """加载商品数据到编辑界面"""
        self._product = product

        self._title_input.setText(product.title)
        self._price_input.setText(str(product.price))

        # SKU
        if product.sku_list:
            self._sku_table.set_data(product.sku_list)
        else:
            self._sku_table.clear()

        # 属性
        if product.attributes:
            self._attr_form.set_attributes(product.attributes)
        else:
            self._attr_form.clear()

        # 图片
        if product.local_images:
            self._image_preview.set_images(product.local_images)
        elif product.original_images:
            # 只有URL没有本地图片，显示提示
            self._image_preview.clear()

        # 店铺信息
        self._shop_label.setText(f"店铺：{product.shop_name or '未知'}")
        self._source_label.setText(f"来源：{product.source_url}")

    def _on_confirm(self):
        """确认上架"""
        if not self._product:
            return

        # 收集编辑后的数据
        self._product.title = self._title_input.text().strip()
        try:
            self._product.price = float(self._price_input.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的价格")
            return

        # 收集SKU
        self._product.sku_list = self._sku_table.get_data()

        # 收集属性
        self._product.attributes = self._attr_form.get_attributes()

        # 校验
        errors = self._product.validate()
        if errors:
            QMessageBox.warning(self, "数据校验", "\n".join(errors))
            return

        self.confirm_clicked.emit(self._product)
