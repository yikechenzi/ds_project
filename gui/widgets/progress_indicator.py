"""
步骤进度条组件
显示多步骤流程的当前进度
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class StepWidget(QWidget):
    """单个步骤指示器"""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._state = "pending"  # pending / active / done
        self.setFixedSize(120, 60)

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str):
        self._state = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 圆圈颜色
        colors = {
            "pending": QColor(180, 180, 180),
            "active": QColor(66, 133, 244),
            "done": QColor(60, 180, 75),
        }
        color = colors.get(self._state, QColor(180, 180, 180))

        # 画圆
        cx, cy = self.width() // 2, 20
        radius = 12
        painter.setBrush(color)
        painter.setPen(QPen(color.darker(120), 2))
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # 圆内状态符号
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        if self._state == "done":
            painter.drawText(cx - 4, cy + 5, "✓")
        elif self._state == "active":
            painter.drawText(cx - 3, cy + 4, "●")
        else:
            painter.drawText(cx - 3, cy + 4, "·")

        # 文字标签
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        font = QFont("Microsoft YaHei", 9)
        painter.setFont(font)
        painter.drawText(0, cy + radius + 6, self.width(), 20, Qt.AlignmentFlag.AlignCenter, self._label)

        painter.end()


class ProgressIndicator(QWidget):
    """多步骤进度指示器"""

    def __init__(self, steps: list = None, parent=None):
        super().__init__(parent)
        self._steps_data = steps or ["采集", "审核", "上架"]
        self._current = 0
        self._step_widgets = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        for i, label in enumerate(self._steps_data):
            step = StepWidget(label)
            self._step_widgets.append(step)
            layout.addWidget(step)

            # 连接线（除了最后一个）
            if i < len(self._steps_data) - 1:
                line = QLabel()
                line.setFixedWidth(40)
                line.setFixedHeight(2)
                line.setStyleSheet("background-color: #cccccc;")
                layout.addWidget(line)

        self._update_visual()

    def set_current(self, index: int):
        """设置当前步骤"""
        self._current = max(0, min(index, len(self._step_widgets) - 1))
        self._update_visual()

    def advance(self):
        """前进到下一步"""
        if self._current < len(self._step_widgets) - 1:
            self._current += 1
            self._update_visual()

    def complete_current(self):
        """标记当前步骤为已完成"""
        if self._current < len(self._step_widgets):
            self._step_widgets[self._current].state = "done"
            self.advance()

    def _update_visual(self):
        """更新视觉状态"""
        for i, sw in enumerate(self._step_widgets):
            if i < self._current:
                sw.state = "done"
            elif i == self._current:
                sw.state = "active"
            else:
                sw.state = "pending"

    @property
    def current_step(self) -> int:
        return self._current
