"""Enhanced 3D pose visualizer widget for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math


class PoseVisualizerGL(QOpenGLWidget):
    """Enhanced OpenGL widget for 3D hexapod visualization."""

    def __init__(self, parent=None):
        """
        Initialize OpenGL visualizer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.rotation_x = 20
        self.rotation_y = 45
        self.zoom = -25
        self.last_pos = None

        # Animation state
        self.animation_phase = 0.0
        self.leg_phases = [0, 60, 120, 180, 240, 300]  # Phase offset for each leg

    def initializeGL(self) -> None:
        """Initialize OpenGL with enhanced settings."""
        glClearColor(0.08, 0.08, 0.10, 1.0)  # Darker blue-tinted background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Smooth shading
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)

        # Anti-aliasing hints
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        # Main light (key light)
        glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 15.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.35, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.95, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])

        # Fill light
        glLightfv(GL_LIGHT1, GL_POSITION, [-5.0, 5.0, -5.0, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.1, 0.1, 0.15, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.4, 0.4, 0.5, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])

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
        """Paint enhanced OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Camera position
        glTranslatef(0.0, -2.0, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # Draw ground plane for reference
        self._draw_ground_plane()

        # Draw hexapod
        self._draw_hexapod()

    def _draw_ground_plane(self) -> None:
        """Draw a subtle ground plane grid."""
        glDisable(GL_LIGHTING)
        glColor4f(0.15, 0.15, 0.2, 0.3)

        grid_size = 30
        grid_spacing = 2.0

        glBegin(GL_LINES)
        for i in range(-grid_size // 2, grid_size // 2 + 1):
            x = i * grid_spacing
            # Lines parallel to X axis
            glVertex3f(-grid_size * grid_spacing / 2, -3.5, x)
            glVertex3f(grid_size * grid_spacing / 2, -3.5, x)
            # Lines parallel to Z axis
            glVertex3f(x, -3.5, -grid_size * grid_spacing / 2)
            glVertex3f(x, -3.5, grid_size * grid_spacing / 2)
        glEnd()

        glEnable(GL_LIGHTING)

    def _draw_hexapod(self) -> None:
        """Draw realistic hexapod robot with black chassis and yellow legs."""
        # Draw main body (black chassis)
        self._draw_chassis()

        # Draw 6 legs (yellow)
        leg_angles = [30, 90, 150, 210, 270, 330]

        for i, leg_angle in enumerate(leg_angles):
            glPushMatrix()
            glRotatef(leg_angle, 0.0, 1.0, 0.0)
            self._draw_leg(i)
            glPopMatrix()

    def _draw_chassis(self) -> None:
        """Draw hexagonal chassis (black)."""
        # Set material properties for black plastic
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.15, 0.15, 0.15, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)

        glColor3f(0.1, 0.1, 0.1)  # Dark black/gray

        body_radius = 3.5
        body_height = 1.2
        num_sides = 6

        # Top surface
        glBegin(GL_POLYGON)
        glNormal3f(0.0, 1.0, 0.0)
        for i in range(num_sides):
            angle = i * 60 * math.pi / 180
            x = body_radius * math.cos(angle)
            z = body_radius * math.sin(angle)
            glVertex3f(x, body_height / 2, z)
        glEnd()

        # Bottom surface
        glBegin(GL_POLYGON)
        glNormal3f(0.0, -1.0, 0.0)
        for i in range(num_sides - 1, -1, -1):
            angle = i * 60 * math.pi / 180
            x = body_radius * math.cos(angle)
            z = body_radius * math.sin(angle)
            glVertex3f(x, -body_height / 2, z)
        glEnd()

        # Side panels with beveled edges
        for i in range(num_sides):
            angle1 = i * 60 * math.pi / 180
            angle2 = ((i + 1) % num_sides) * 60 * math.pi / 180

            x1 = body_radius * math.cos(angle1)
            z1 = body_radius * math.sin(angle1)
            x2 = body_radius * math.cos(angle2)
            z2 = body_radius * math.sin(angle2)

            # Calculate normal for this face
            dx = x2 - x1
            dz = z2 - z1
            normal_x = -dz
            normal_z = dx
            length = math.sqrt(normal_x**2 + normal_z**2)
            if length > 0:
                normal_x /= length
                normal_z /= length

            glBegin(GL_QUADS)
            glNormal3f(normal_x, 0.0, normal_z)
            glVertex3f(x1, body_height / 2, z1)
            glVertex3f(x2, body_height / 2, z2)
            glVertex3f(x2, -body_height / 2, z2)
            glVertex3f(x1, -body_height / 2, z1)
            glEnd()

        # Central hub detail
        glColor3f(0.08, 0.08, 0.08)
        self._draw_cylinder_at(0, 0, 0, 0.8, body_height + 0.2, axis="y")

    def _draw_leg(self, leg_index: int) -> None:
        """
        Draw a single articulated leg with yellow color.

        Args:
            leg_index: Index of the leg (0-5)
        """
        # Set material properties for yellow plastic/metal
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.3, 0.25, 0.0, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 0.85, 0.1, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.8, 0.8, 0.4, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 64.0)

        glColor3f(1.0, 0.85, 0.1)  # Bright yellow

        # Animation parameters
        phase = (self.animation_phase + self.leg_phases[leg_index]) * math.pi / 180
        coxa_angle = math.sin(phase) * 5
        femur_angle = -30 + math.sin(phase) * 10
        tibia_angle = -60 + math.cos(phase) * 15

        # Coxa (hip joint)
        glPushMatrix()
        glTranslatef(3.5, 0.0, 0.0)

        # Hip joint sphere
        glColor3f(0.2, 0.2, 0.2)
        self._draw_sphere(0.4)

        glColor3f(1.0, 0.85, 0.1)
        glRotatef(coxa_angle, 0.0, 1.0, 0.0)

        # Coxa segment
        glPushMatrix()
        glTranslatef(0.8, 0.0, 0.0)
        self._draw_cylinder_at(-0.8, 0, 0, 0.35, 1.6, axis="x")
        glPopMatrix()

        # Femur (thigh)
        glTranslatef(1.6, 0.0, 0.0)

        # Knee joint sphere
        glColor3f(0.2, 0.2, 0.2)
        self._draw_sphere(0.35)

        glColor3f(1.0, 0.85, 0.1)
        glRotatef(femur_angle, 0.0, 0.0, 1.0)

        # Femur segment
        glPushMatrix()
        glTranslatef(1.2, 0.0, 0.0)
        self._draw_cylinder_at(-1.2, 0, 0, 0.3, 2.4, axis="x")
        glPopMatrix()

        # Tibia (shin)
        glTranslatef(2.4, 0.0, 0.0)

        # Ankle joint sphere
        glColor3f(0.2, 0.2, 0.2)
        self._draw_sphere(0.3)

        glColor3f(1.0, 0.85, 0.1)
        glRotatef(tibia_angle, 0.0, 0.0, 1.0)

        # Tibia segment
        glPushMatrix()
        glTranslatef(1.2, 0.0, 0.0)
        self._draw_cylinder_at(-1.2, 0, 0, 0.25, 2.4, axis="x")
        glPopMatrix()

        # Foot
        glTranslatef(2.4, 0.0, 0.0)
        glColor3f(0.15, 0.15, 0.15)
        self._draw_sphere(0.35)

        glPopMatrix()

    def _draw_sphere(self, radius: float, slices: int = 16, stacks: int = 16) -> None:
        """
        Draw a sphere.

        Args:
            radius: Sphere radius
            slices: Number of slices
            stacks: Number of stacks
        """
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

    def _draw_cylinder_at(
        self,
        x: float,
        y: float,
        z: float,
        radius: float,
        length: float,
        axis: str = "x",
        slices: int = 16,
    ) -> None:
        """
        Draw a cylinder at a specific position along an axis.

        Args:
            x, y, z: Position
            radius: Cylinder radius
            length: Cylinder length
            axis: Axis to align along ('x', 'y', or 'z')
            slices: Number of slices for smoothness
        """
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)

        glPushMatrix()
        glTranslatef(x, y, z)

        if axis == "x":
            glRotatef(90, 0.0, 1.0, 0.0)
        elif axis == "y":
            glRotatef(-90, 1.0, 0.0, 0.0)
        # 'z' is default orientation

        gluCylinder(quadric, radius, radius, length, slices, 1)

        # Draw caps
        gluDisk(quadric, 0, radius, slices, 1)
        glTranslatef(0, 0, length)
        gluDisk(quadric, 0, radius, slices, 1)

        glPopMatrix()
        gluDeleteQuadric(quadric)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press."""
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for rotation."""
        if self.last_pos is not None:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()

            if event.buttons() & Qt.LeftButton:
                self.rotation_y += dx * 0.5
                self.rotation_x += dy * 0.5
                # Clamp rotation_x to prevent flipping
                self.rotation_x = max(-89, min(89, self.rotation_x))
                self.update()

            self.last_pos = event.pos()

    def wheelEvent(self, event) -> None:
        """Handle mouse wheel for zoom."""
        delta = event.angleDelta().y()
        self.zoom += delta / 60.0
        self.zoom = max(-60, min(-10, self.zoom))
        self.update()

    def update_animation(self, phase: float) -> None:
        """
        Update animation phase.

        Args:
            phase: Animation phase in degrees
        """
        self.animation_phase = phase
        self.update()


class PoseVisualizer(QWidget):
    """Enhanced 3D pose visualizer widget."""

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

        # Title bar with enhanced styling
        title = QLabel("3D Pose Visualization")
        title.setStyleSheet(
            """
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                color: #ffd700;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-bottom: 2px solid #ffd700;
            }
        """
        )

        # OpenGL widget
        self.gl_widget = PoseVisualizerGL()
        self.gl_widget.setMinimumSize(500, 500)
        self.gl_widget.setStyleSheet(
            """
            QOpenGLWidget {
                border: 1px solid #3a3a3a;
                background-color: #0a0a0c;
            }
        """
        )

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(33)  # ~30 FPS

        self.animation_phase = 0.0

        layout.addWidget(title)
        layout.addWidget(self.gl_widget, 1)

        self.setLayout(layout)

    def _animate(self) -> None:
        """Animate the visualization."""
        # Smooth walking animation
        self.animation_phase += 1.5
        if self.animation_phase >= 360:
            self.animation_phase -= 360

        self.gl_widget.update_animation(self.animation_phase)

        # Subtle automatic rotation
        self.gl_widget.rotation_y += 0.3
        if self.gl_widget.rotation_y >= 360:
            self.gl_widget.rotation_y -= 360
