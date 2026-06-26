"""
商品属性表单组件
支持属性的查看和编辑
"""
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QLabel, QVBoxLayout,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, Signal


class AttributeForm(QWidget):
    """商品属性编辑表单"""

    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fields = {}  # {name: QLineEdit}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._form_widget = QWidget()
        self._form_layout = QFormLayout(self._form_widget)
        self._form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self._form_layout.setSpacing(8)
        scroll.setWidget(self._form_widget)
        layout.addWidget(scroll)

    def set_attributes(self, attributes: dict):
        """加载属性数据"""
        self._clear_fields()
        for name, value in attributes.items():
            line_edit = QLineEdit(str(value))
            line_edit.setPlaceholderText(f"请输入{name}")
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px 8px;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border-color: #4285f4;
                }
            """)
            line_edit.textChanged.connect(lambda: self.data_changed.emit())
            label = QLabel(f"{name}：")
            label.setStyleSheet("font-weight: bold; color: #333;")
            self._form_layout.addRow(label, line_edit)
            self._fields[name] = line_edit

    def get_attributes(self) -> dict:
        """获取编辑后的属性数据"""
        return {name: field.text() for name, field in self._fields.items()}

    def _clear_fields(self):
        """清除所有表单字段"""
        while self._form_layout.rowCount() > 0:
            self._form_layout.removeRow(0)
        self._fields.clear()

    def clear(self):
        """清空表单"""
        self._clear_fields()

    @property
    def field_count(self) -> int:
        return len(self._fields)
