"""Servo matrix widget for SIRA Console."""

import math

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPointF
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QPainterPath,
)
from src.utils.constants import Colors
from src.core.config_loader import ConfigLoader


# ─────────────────────────────────────────────────────────────────────────────
# Deg / Rad toggle
# ─────────────────────────────────────────────────────────────────────────────


class ToggleSwitch(QWidget):
    """Pill-shaped toggle: left = DEG (default), right = RAD."""

    toggled = pyqtSignal(bool)  # True = radians

    _PADDING = 4
    _PILL_H = 22
    _PILL_W = 72
    _KNOB_SIZE = 14

    def __init__(self, parent=None):
        super().__init__(parent)
        self._radians = False
        self.setFixedSize(self._PILL_W, self._PILL_H)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Toggle degrees / radians")

    def is_radians(self) -> bool:
        return self._radians

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._radians = not self._radians
            self.toggled.emit(self._radians)
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = h / 2
        track_color = (
            QColor(Colors.ACCENT_YELLOW)
            if self._radians
            else QColor(Colors.SECONDARY_BG)
        )
        p.setPen(QPen(QColor(Colors.BORDER), 1))
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(0, 0, w, h, r, r)
        knob_x = (
            (w - self._KNOB_SIZE - self._PADDING) if self._radians else self._PADDING
        )
        knob_y = (h - self._KNOB_SIZE) // 2
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(Colors.TEXT_PRIMARY)))
        p.drawEllipse(knob_x, knob_y, self._KNOB_SIZE, self._KNOB_SIZE)
        font = QFont()
        font.setPointSize(7)
        font.setBold(True)
        p.setFont(font)
        if self._radians:
            p.setPen(QColor(Colors.PANEL_BG))
            p.drawText(QRect(4, 0, w // 2, h), Qt.AlignCenter, "RAD")
        else:
            p.setPen(QColor(Colors.TEXT_SECONDARY))
            p.drawText(QRect(w // 2, 0, w // 2, h), Qt.AlignCenter, "DEG")
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Column header  (FRONT / LEFT  stacked)
# ─────────────────────────────────────────────────────────────────────────────


class LimbHeader(QWidget):
    """Diamond-accented two-line column header."""

    def __init__(self, line1: str, line2: str, parent=None):
        super().__init__(parent)
        self.line1 = line1.upper()
        self.line2 = line2.upper()
        self.setMinimumWidth(80)
        self.setFixedHeight(58)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Bottom rule
        p.setPen(QPen(QColor(Colors.BORDER), 1))
        p.drawLine(6, h - 1, w - 6, h - 1)

        # Diamond accent at top-centre
        diamond_r = 6
        cx = w / 2
        path = QPainterPath()
        path.moveTo(cx, 4)
        path.lineTo(cx + diamond_r, 4 + diamond_r)
        path.lineTo(cx, 4 + diamond_r * 2)
        path.lineTo(cx - diamond_r, 4 + diamond_r)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(Colors.ACCENT_YELLOW)))
        p.drawPath(path)

        # Line 1
        f1 = QFont()
        f1.setPointSize(11)
        f1.setBold(True)
        p.setFont(f1)
        p.setPen(QColor(Colors.TEXT_PRIMARY))
        p.drawText(QRect(0, 17, w, 20), Qt.AlignHCenter | Qt.AlignVCenter, self.line1)

        # Line 2
        f2 = QFont()
        f2.setPointSize(9)
        p.setFont(f2)
        p.setPen(QColor(Colors.TEXT_SECONDARY))
        p.drawText(QRect(0, 37, w, 18), Qt.AlignHCenter | Qt.AlignVCenter, self.line2)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Row header  (HIP / THIGH / TIBIA)  — QLabel-based, always visible
# ─────────────────────────────────────────────────────────────────────────────


class JointHeader(QWidget):
    """Row label with yellow accent bar — stable, no paint glitches."""

    BAR_WIDTH = 3

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # ---- TEXT LABEL ----
        label = QLabel(name.upper())
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 12pt;
                font-weight: bold;
                background: transparent;
                padding: 2pt;
            }}
            """
        )

        # ---- ACCENT BAR ----
        accent = QWidget()
        accent.setFixedWidth(self.BAR_WIDTH)
        accent.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        accent.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.ACCENT_YELLOW};
                border-radius: 1px;
            }}
            """
        )

        layout.addWidget(label, 1)
        layout.addWidget(accent)


# ─────────────────────────────────────────────────────────────────────────────
# Speedometer dial  — display + interactive drag in test mode
# ─────────────────────────────────────────────────────────────────────────────
#
# Arc geometry:
#   Centre of the widget.  270° sweep, starting at 225° (bottom-left),
#   going clockwise to 315° (bottom-right).  min_angle maps to 225°,
#   max_angle maps to 315°.
#
#   Mouse drag:  compute the angle of the cursor relative to the centre,
#   snap it to the arc range, convert back to servo degrees.


class _SpeedometerDial(QWidget):
    """
    Circular speedometer that is also draggable in test mode.
    In display mode: read-only arc + value.
    In test mode: drag the knob along the arc to change the angle.
    """

    angle_changed = pyqtSignal(int)

    # Arc geometry constants
    _ARC_START = 225  # degrees (bottom-left), where min_angle lives
    _ARC_SWEEP = 270  # total sweep clockwise

    def __init__(self, angle, min_angle, max_angle, safe_min, safe_max, parent=None):
        super().__init__(parent)
        self._angle = angle
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._safe_min = safe_min
        self._safe_max = safe_max
        self._radians = False
        self._test_mode = False
        self._dragging = False
        self.setCursor(Qt.ArrowCursor)

    # ── public setters ────────────────────────────────────────────────────────

    def set_angle(self, angle: int) -> None:
        self._angle = max(self._min_angle, min(self._max_angle, angle))
        self.update()

    def set_show_radians(self, radians: bool) -> None:
        self._radians = radians
        self.update()

    def set_test_mode(self, enabled: bool) -> None:
        self._test_mode = enabled
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)
        self.update()

    # ── geometry helpers ──────────────────────────────────────────────────────

    def _arc_rect(self) -> QRect:
        """Bounding rect for the arc, leaving margin."""
        m = 6
        return QRect(m, m, self.width() - m * 2, self.height() - m * 2)

    def _zone_color(self) -> QColor:
        if self._angle < self._safe_min or self._angle > self._safe_max:
            return QColor(Colors.STATUS_RED)
        if self._angle < self._safe_min + 10 or self._angle > self._safe_max - 10:
            return QColor(Colors.ACCENT_YELLOW)
        return QColor(Colors.STATUS_GREEN)

    def _servo_to_arc_deg(self, servo_angle: int) -> float:
        """Convert servo angle → arc angle in standard Qt degrees (counter-clockwise from 3 o'clock)."""
        total = self._max_angle - self._min_angle or 1
        frac = (servo_angle - self._min_angle) / total
        # _ARC_START is measured clockwise from 3 o'clock (Qt convention: negative = clockwise)
        # We go clockwise so subtract
        arc_deg = self._ARC_START - frac * self._ARC_SWEEP
        return arc_deg

    def _cursor_to_servo(self, pos: QPointF) -> int:
        """Convert cursor position → servo angle by measuring angle from widget centre."""
        cx = self.width() / 2
        cy = self.height() / 2
        dx = pos.x() - cx
        dy = pos.y() - cy
        # atan2 gives CCW from 3 o'clock in radians; convert to CW degrees from 3 o'clock
        deg = -math.degrees(math.atan2(-dy, dx))  # clockwise from 3 o'clock
        if deg < 0:
            deg += 360

        # Map into arc: _ARC_START going clockwise _ARC_SWEEP degrees
        # arc_pos = how far CW we are from the start of the arc (225° CW from 3 o'clock)
        arc_pos = (self._ARC_START - deg) % 360
        # Clamp to arc sweep
        arc_pos = max(0.0, min(float(self._ARC_SWEEP), arc_pos))
        frac = arc_pos / self._ARC_SWEEP
        servo = int(round(self._min_angle + frac * (self._max_angle - self._min_angle)))
        return max(self._min_angle, min(self._max_angle, servo))

    def _knob_centre(self) -> QPointF:
        """Pixel position of the draggable knob."""
        rect = self._arc_rect()
        cx = rect.x() + rect.width() / 2
        cy = rect.y() + rect.height() / 2
        r = rect.width() / 2 - 4  # slightly inset from the arc
        arc_deg = self._servo_to_arc_deg(self._angle)
        rad = math.radians(arc_deg)
        return QPointF(cx + r * math.cos(rad), cy - r * math.sin(rad))

    # ── mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if not self._test_mode:
            return
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._update_from_pos(event.pos())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False

    def _update_from_pos(self, pos):
        new_angle = self._cursor_to_servo(QPointF(pos))
        if new_angle != self._angle:
            self._angle = new_angle
            self.update()
            self.angle_changed.emit(self._angle)

    # ── painting ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        rect = self._arc_rect()
        color = self._zone_color()

        # ── background circle ──
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(Colors.PANEL_BG)))
        p.drawEllipse(rect)

        # ── dim track arc (full sweep, grey) ──
        track_pen = QPen(QColor(Colors.BORDER), 4, Qt.SolidLine, Qt.RoundCap)
        p.setPen(track_pen)
        p.setBrush(Qt.NoBrush)
        inner = rect.adjusted(5, 5, -5, -5)
        p.drawArc(inner, self._ARC_START * 16, -self._ARC_SWEEP * 16)

        # ── filled arc showing current position ──
        total = self._max_angle - self._min_angle or 1
        frac = (self._angle - self._min_angle) / total
        filled = int(frac * self._ARC_SWEEP)
        value_pen = QPen(color, 4, Qt.SolidLine, Qt.RoundCap)
        p.setPen(value_pen)
        p.drawArc(inner, self._ARC_START * 16, -filled * 16)

        # ── border ring ──
        p.setPen(QPen(QColor(Colors.BORDER), 1))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(rect)

        # ── centre value text ──
        if self._radians:
            text = f"{math.radians(self._angle):.2f}"
            font_pt = 9
        else:
            text = f"{self._angle}°"
            font_pt = 11

        f = QFont()
        f.setPointSize(font_pt)
        f.setBold(True)
        p.setFont(f)
        p.setPen(color)
        # Draw text in the inner circle — nudge up slightly to leave room below
        text_rect = QRect(rect.x(), rect.y() - 6, rect.width(), rect.height())
        p.drawText(text_rect, Qt.AlignCenter, text)

        # ── draggable knob (test mode only) ──
        if self._test_mode:
            kc = self._knob_centre()
            kr = 6
            # outer glow ring
            p.setPen(QPen(color, 1))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(
                QRect(
                    int(kc.x() - kr - 2),
                    int(kc.y() - kr - 2),
                    (kr + 2) * 2,
                    (kr + 2) * 2,
                )
            )
            # filled knob
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(QRect(int(kc.x() - kr), int(kc.y() - kr), kr * 2, kr * 2))
            # white centre dot
            p.setBrush(QBrush(QColor(Colors.TEXT_PRIMARY)))
            p.drawEllipse(QRect(int(kc.x() - 2), int(kc.y() - 2), 4, 4))

            # small "drag" hint text at the bottom
            fh = QFont()
            fh.setPointSize(7)
            p.setFont(fh)
            p.setPen(QColor(Colors.TEXT_SECONDARY))
            p.drawText(QRect(0, h - 14, w, 14), Qt.AlignCenter, "drag")

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# ServoControl  — wraps the dial
# ─────────────────────────────────────────────────────────────────────────────


class ServoControl(QWidget):
    """Individual servo control — speedometer dial, draggable in test mode."""

    angle_changed = pyqtSignal(int)

    _DIAL_SIZE = 86

    def __init__(
        self,
        joint_name: str,
        default_angle: int,
        min_angle: int,
        max_angle: int,
        safe_min: int,
        safe_max: int,
        parent=None,
    ):
        super().__init__(parent)
        self.joint_name = joint_name
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.safe_min = safe_min
        self.safe_max = safe_max
        self._current_angle = default_angle
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignHCenter)

        self._dial = _SpeedometerDial(
            self._current_angle,
            self.min_angle,
            self.max_angle,
            self.safe_min,
            self.safe_max,
        )
        self._dial.setFixedSize(self._DIAL_SIZE, self._DIAL_SIZE)
        self._dial.angle_changed.connect(self._on_dial_changed)

        layout.addWidget(self._dial, 0, Qt.AlignHCenter)
        self.setLayout(layout)

    def set_show_radians(self, radians: bool) -> None:
        self._dial.set_show_radians(radians)

    def set_test_mode(self, enabled: bool) -> None:
        self._dial.set_test_mode(enabled)

    def set_angle(self, angle: int) -> None:
        self._current_angle = angle
        self._dial.set_angle(angle)

    def get_angle(self) -> int:
        return self._current_angle

    def _on_dial_changed(self, value: int) -> None:
        self._current_angle = value
        self.angle_changed.emit(value)


# ─────────────────────────────────────────────────────────────────────────────
# Servo Matrix
# ─────────────────────────────────────────────────────────────────────────────


class ServoMatrix(QWidget):
    """Servo matrix widget showing all servo controls."""

    def __init__(self, config: ConfigLoader, parent=None):
        super().__init__(parent)
        self.config = config
        self._test_mode = False
        self._servo_controls = []
        self._show_radians = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ── Title row ────────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Servo Matrix")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 10pt;
                font-weight: bold;
            }}
            """
        )

        self._toggle = ToggleSwitch()
        self._toggle.toggled.connect(self._on_unit_toggled)

        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self._toggle)

        # ── Grid frame ───────────────────────────────────────────────────────
        grid_frame = QFrame()
        grid_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.SECONDARY_BG};
                border: 1px solid {Colors.BORDER};
            }}
            """
        )
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        limb_names = self.config.get_servo_param("limb_names", default=[])
        joint_names = self.config.get_servo_param("joint_names", default=[])
        servo_defaults = self.config.get_servo_param("servo_defaults", default={})

        # Column headers
        for col, limb_name in enumerate(limb_names):
            parts = limb_name.split()
            l1 = parts[0] if parts else limb_name
            l2 = parts[1] if len(parts) > 1 else ""
            header = LimbHeader(l1, l2)
            grid_layout.addWidget(header, 0, col + 1, Qt.AlignHCenter)

        # Row headers + servo controls
        for row, joint_name in enumerate(joint_names):
            row_header = JointHeader(joint_name)
            grid_layout.addWidget(
                row_header, row + 1, 0, Qt.AlignVCenter | Qt.AlignHCenter
            )

            joint_key = joint_name.lower()
            joint_config = servo_defaults.get(joint_key, {})
            default_angle = joint_config.get("default_angle", 0)
            min_angle = joint_config.get("min_angle", 0)
            max_angle = joint_config.get("max_angle", 180)
            safe_min = joint_config.get("safe_min", 10)
            safe_max = joint_config.get("safe_max", 170)

            for col in range(6):
                servo = ServoControl(
                    joint_name, default_angle, min_angle, max_angle, safe_min, safe_max
                )
                self._servo_controls.append(servo)
                grid_layout.addWidget(
                    servo, row + 1, col + 1, Qt.AlignHCenter | Qt.AlignVCenter
                )

        layout.addLayout(title_row)
        layout.addWidget(grid_frame, 1)
        self.setLayout(layout)

    # ── slots / public API ────────────────────────────────────────────────────

    def _on_unit_toggled(self, radians: bool) -> None:
        self._show_radians = radians
        for servo in self._servo_controls:
            servo.set_show_radians(radians)

    def set_test_mode(self, enabled: bool) -> None:
        self._test_mode = enabled
        for servo in self._servo_controls:
            servo.set_test_mode(enabled)

    def set_servo_angle(self, limb: int, joint: int, angle: int) -> None:
        index = limb + joint * 6
        if 0 <= index < len(self._servo_controls):
            self._servo_controls[index].set_angle(angle)

    def get_servo_angle(self, limb: int, joint: int) -> int:
        index = limb + joint * 6
        if 0 <= index < len(self._servo_controls):
            return self._servo_controls[index].get_angle()
        return 0

    def reset_all(self) -> None:
        """Reset all servos to default angles."""
        joint_names = self.config.get_servo_param("joint_names", default=[])
        servo_defaults = self.config.get_servo_param("servo_defaults", default={})

        for joint_idx, joint_name in enumerate(joint_names):
            joint_key = joint_name.lower()
            joint_config = servo_defaults.get(joint_key, {})
            default_angle = joint_config.get("default_angle", 0)
            for limb_idx in range(6):
                self.set_servo_angle(limb_idx, joint_idx, default_angle)
