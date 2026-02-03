"""3D pose visualizer widget for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math


class PoseVisualizerGL(QOpenGLWidget):
    """OpenGL widget for 3D hexapod visualization."""

    def __init__(self, parent=None):
        """
        Initialize OpenGL visualizer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.rotation_x = 30
        self.rotation_y = 45
        self.zoom = -20
        self.last_pos = None

    def initializeGL(self) -> None:
        """Initialize OpenGL."""
        glClearColor(0.04, 0.04, 0.04, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        # Light properties
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

    def resizeGL(self, w: int, h: int) -> None:
        """
        Handle resize.

        Args:
            w: Width
            h: Height
        """
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h > 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        """Paint OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Camera position
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # Draw hexapod
        self._draw_hexapod()

    def _draw_hexapod(self) -> None:
        """Draw simplified hexapod robot."""
        # Body (hexagon)
        glColor3f(0.7, 0.7, 0.7)
        body_radius = 3.0

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, 0.5, 0.0)
        for i in range(7):
            angle = i * 60 * math.pi / 180
            x = body_radius * math.cos(angle)
            z = body_radius * math.sin(angle)
            glVertex3f(x, 0.5, z)
        glEnd()

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, -0.5, 0.0)
        for i in range(7):
            angle = i * 60 * math.pi / 180
            x = body_radius * math.cos(angle)
            z = body_radius * math.sin(angle)
            glVertex3f(x, -0.5, z)
        glEnd()

        # Draw 6 legs
        leg_angles = [30, 90, 150, 210, 270, 330]

        for leg_angle in leg_angles:
            glPushMatrix()
            glRotatef(leg_angle, 0.0, 1.0, 0.0)
            self._draw_leg()
            glPopMatrix()

    def _draw_leg(self) -> None:
        """Draw a single leg."""
        glColor3f(1.0, 0.77, 0.03)  # Yellow

        # Hip
        glPushMatrix()
        glTranslatef(3.0, 0.0, 0.0)
        self._draw_cylinder(0.3, 1.5)

        # Thigh
        glTranslatef(1.5, 0.0, 0.0)
        glRotatef(-30, 0.0, 0.0, 1.0)
        glTranslatef(1.0, 0.0, 0.0)
        self._draw_cylinder(0.25, 2.0)

        # Tibia
        glTranslatef(2.0, 0.0, 0.0)
        glRotatef(-60, 0.0, 0.0, 1.0)
        glTranslatef(1.0, 0.0, 0.0)
        self._draw_cylinder(0.2, 2.0)

        glPopMatrix()

    def _draw_cylinder(self, radius: float, length: float) -> None:
        """
        Draw a cylinder.

        Args:
            radius: Cylinder radius
            length: Cylinder length
        """
        quadric = gluNewQuadric()
        glPushMatrix()
        glRotatef(90, 0.0, 1.0, 0.0)
        gluCylinder(quadric, radius, radius, length, 8, 1)
        glPopMatrix()
        gluDeleteQuadric(quadric)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press."""
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move."""
        if self.last_pos is not None:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()

            if event.buttons() & Qt.LeftButton:
                self.rotation_y += dx
                self.rotation_x += dy
                self.update()

            self.last_pos = event.pos()

    def wheelEvent(self, event) -> None:
        """Handle mouse wheel."""
        delta = event.angleDelta().y()
        self.zoom += delta / 120.0
        self.zoom = max(-50, min(-5, self.zoom))
        self.update()


class PoseVisualizer(QWidget):
    """3D pose visualizer widget."""

    def __init__(self, parent=None):
        """
        Initialize pose visualizer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title = QLabel("3D Pose Visualization")
        title.setStyleSheet(
            f"""
            QLabel {{
                background-color: #1a1a1a;
                color: #a0a0a0;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #2a2a2a;
                border-bottom: none;
            }}
        """
        )

        # OpenGL widget
        self.gl_widget = PoseVisualizerGL()
        self.gl_widget.setMinimumSize(400, 400)

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(33)  # ~30 FPS

        layout.addWidget(title)
        layout.addWidget(self.gl_widget, 1)

        self.setLayout(layout)

    def _animate(self) -> None:
        """Animate the visualization."""
        # Slow rotation
        self.gl_widget.rotation_y += 0.5
        self.gl_widget.update()
