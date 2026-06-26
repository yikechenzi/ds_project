"""
图片预览组件
支持多图片缩略图展示和点击查看大图
"""
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy, QDialog, QApplication,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QCursor


class ThumbnailLabel(QLabel):
    """可点击的缩略图"""

    clicked = Signal(int)

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self._index = index
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #f5f5f5;
            }
            QLabel:hover {
                border-color: #4285f4;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._index)


class ImagePreview(QWidget):
    """图片预览面板"""

    image_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._images = []  # 本地图片路径列表
        self._thumbnails = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setMaximumHeight(130)

        self._container = QWidget()
        self._thumb_layout = QHBoxLayout(self._container)
        self._thumb_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._thumb_layout.setSpacing(6)
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        # 大图预览区
        self._preview_label = QLabel("暂无图片")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setMinimumHeight(200)
        self._preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #fafafa;
                color: #999;
            }
        """)
        layout.addWidget(self._preview_label)

    def set_images(self, image_paths: list):
        """设置图片列表"""
        self._images = image_paths
        self._refresh_thumbnails()
        if image_paths:
            self._show_preview(0)

    def _refresh_thumbnails(self):
        """刷新缩略图"""
        # 清除旧缩略图
        for thumb in self._thumbnails:
            thumb.deleteLater()
        self._thumbnails.clear()

        for i, path in enumerate(self._images):
            thumb = ThumbnailLabel(i)
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
                thumb.setPixmap(scaled)
            else:
                thumb.setText(f"图{i+1}")
            thumb.clicked.connect(self._show_preview)
            self._thumb_layout.addWidget(thumb)
            self._thumbnails.append(thumb)

    def _show_preview(self, index: int):
        """显示大图预览"""
        if 0 <= index < len(self._images):
            path = self._images[index]
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    500, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._preview_label.setPixmap(scaled)
            self.image_selected.emit(index)

    def clear(self):
        """清空预览"""
        self._images.clear()
        for thumb in self._thumbnails:
            thumb.deleteLater()
        self._thumbnails.clear()
        self._preview_label.clear()
        self._preview_label.setText("暂无图片")
