"""Remote control widget for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPaintEvent, QMouseEvent
from src.utils.constants import Colors
from src.utils.constants import Dimensions
import math


class RemoteControlJoystick(QWidget):
    """Joystick control widget."""

    position_changed = pyqtSignal(float, float)  # x, y in range [-1, 1]

    def __init__(self, parent=None):
        """
        Initialize joystick.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._center = QPointF(100, 100)
        self._handle_pos = QPointF(100, 100)
        self._dragging = False
        self._max_radius = 80
        self._initialized = False

    def resizeEvent(self, event) -> None:
        """
        Handle resize event to update center position.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)
        self._center = QPointF(self.width() / 2, self.height() / 2)
        self._max_radius = min(self.width(), self.height()) / 2 - 20
        if not self._dragging:
            self._handle_pos = QPointF(self._center)
        self._initialized = True

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the joystick.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Ensure center is initialized
        if not self._initialized:
            self._center = QPointF(self.width() / 2, self.height() / 2)
            self._max_radius = min(self.width(), self.height()) / 2 - 20
            self._handle_pos = QPointF(self._center)
            self._initialized = True

        # Draw outer circle
        painter.setPen(QPen(QColor(Colors.BORDER), 2))
        painter.setBrush(QBrush(QColor(Colors.PANEL_BG)))
        painter.drawEllipse(self._center, self._max_radius, self._max_radius)

        # Draw center cross
        painter.setPen(QPen(QColor(Colors.TEXT_SECONDARY), 1))
        painter.drawLine(
            int(self._center.x() - 10),
            int(self._center.y()),
            int(self._center.x() + 10),
            int(self._center.y()),
        )
        painter.drawLine(
            int(self._center.x()),
            int(self._center.y() - 10),
            int(self._center.x()),
            int(self._center.y() + 10),
        )

        # Draw handle
        painter.setPen(QPen(QColor(Colors.ACCENT_YELLOW), 2))
        painter.setBrush(QBrush(QColor(Colors.ACCENT_YELLOW)))
        painter.drawEllipse(self._handle_pos, 15, 15)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._update_handle_position(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move.

        Args:
            event: Mouse event
        """
        if self._dragging:
            self._update_handle_position(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse release.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self._handle_pos = QPointF(self._center)
            self.update()
            self.position_changed.emit(0.0, 0.0)

    def _update_handle_position(self, pos: QPointF) -> None:
        """
        Update handle position based on mouse.

        Args:
            pos: Mouse position
        """
        dx = pos.x() - self._center.x()
        dy = pos.y() - self._center.y()
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > self._max_radius:
            ratio = self._max_radius / distance
            dx *= ratio
            dy *= ratio
            distance = self._max_radius

        self._handle_pos = QPointF(self._center.x() + dx, self._center.y() + dy)
        self.update()

        # Emit normalized position
        norm_x = dx / self._max_radius
        norm_y = -dy / self._max_radius  # Invert Y for intuitive up/down
        self.position_changed.emit(norm_x, norm_y)


class RemoteControl(QWidget):
    """Remote control widget with joystick and gait display."""

    def __init__(self, parent=None):
        """
        Initialize remote control.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_x = 0.0
        self._current_y = 0.0
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)

        # Set minimum width to match sensor display
        self.setMinimumWidth(Dimensions.DASHBOARD_SIDEBAR)

        # Title
        title = QLabel("Remote Control")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )
        title.setAlignment(Qt.AlignCenter)

        # Joystick (centered and sized to match sensor display)
        self.joystick = RemoteControlJoystick()
        self.joystick.setSizePolicy(
            self.joystick.sizePolicy().horizontalPolicy(),
            self.joystick.sizePolicy().verticalPolicy(),
        )

        # Gait record
        gait_layout = QHBoxLayout()

        direction_label = QLabel("Direction:")
        direction_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.direction_value = QLabel("Center")
        self.direction_value.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.direction_value.setMinimumWidth(120)
        self.direction_value.setAlignment(Qt.AlignLeft)

        angle_label = QLabel("Angle:")
        angle_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.angle_value = QLabel("0°")
        self.angle_value.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.angle_value.setMinimumWidth(50)
        self.angle_value.setAlignment(Qt.AlignLeft)

        gait_layout.addWidget(direction_label)
        gait_layout.addWidget(self.direction_value)
        gait_layout.addStretch()
        gait_layout.addWidget(angle_label)
        gait_layout.addWidget(self.angle_value)

        layout.addWidget(title)
        layout.addWidget(self.joystick, 1)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.stall_btn = QPushButton("▲  Stall")
        self.stall_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SECONDARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 4px 16px;
                font-family: {Colors.TEXT_SECONDARY};
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.PANEL_BG};
                border: 1px solid {Colors.STATUS_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {Colors.STATUS_GREEN};
                color: {Colors.PRIMARY_BG};
            }}
        """
        )

        self.rest_btn = QPushButton("▼  Rest")
        self.rest_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Colors.SECONDARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 4px 16px;
                font-family: {Colors.TEXT_SECONDARY};
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.PANEL_BG};
                border: 1px solid {Colors.STATUS_ORANGE};
            }}
            QPushButton:pressed {{
                background-color: {Colors.STATUS_ORANGE};
                color: {Colors.PRIMARY_BG};
            }}
        """
        )

        button_layout.addWidget(self.stall_btn)
        button_layout.addWidget(self.rest_btn)

        layout.addLayout(button_layout)
        layout.addLayout(gait_layout)
        layout.addStretch()

        self.setLayout(layout)
        self.joystick.position_changed.connect(self._on_position_changed)

    def _on_position_changed(self, x: float, y: float) -> None:
        """
        Handle joystick position change.

        Args:
            x: X position [-1, 1]
            y: Y position [-1, 1]
        """
        self._current_x = x
        self._current_y = y

        # Calculate angle and direction
        angle = math.degrees(math.atan2(y, x))
        magnitude = math.sqrt(x * x + y * y)

        if magnitude < 0.1:
            direction = "Center"
        else:
            if abs(y) > abs(x):
                direction = "Forward" if y > 0 else "Backward"
            else:
                direction = "Right" if x > 0 else "Left"

            # Add compound directions
            if magnitude > 0.5:
                if y > 0.3 and x > 0.3:
                    direction = "Forward-Right"
                elif y > 0.3 and x < -0.3:
                    direction = "Forward-Left"
                elif y < -0.3 and x > 0.3:
                    direction = "Backward-Right"
                elif y < -0.3 and x < -0.3:
                    direction = "Backward-Left"

        self.direction_value.setText(direction)
        self.angle_value.setText(f"{angle:.0f}°")
