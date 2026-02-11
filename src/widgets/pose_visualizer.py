"""Clean and physically accurate 3D pose visualizer for SIRA Console hexapod."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QOpenGLWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math


class PoseVisualizerGL(QOpenGLWidget):
    """OpenGL widget for physically accurate hexapod visualization."""

    def __init__(self, parent=None):
        """Initialize OpenGL visualizer."""
        super().__init__(parent)
        self.rotation_x = 20
        self.rotation_y = 45
        self.zoom = -35
        self.last_pos = None

        # Servo angles for 6 legs, 3 joints each (hip, thigh, tibia)
        # Default positions based on specifications
        self.servo_angles = np.zeros((6, 3))
        # Set default angles: hip=90, thigh=120, tibia=0
        self.servo_angles[:, 0] = 90  # Hip
        self.servo_angles[:, 1] = 120  # Thigh
        self.servo_angles[:, 2] = 0  # Tibia

        # Servo limits (min, max, default)
        self.servo_limits = {
            "hip": (40, 150, 90),  # Left-right rotation
            "thigh": (0, 180, 120),  # Up-down, 0=down
            "tibia": (0, 180, 0),  # Up-down, 0=perpendicular down
        }

        # Robot dimensions
        self.body_radius = 4.0
        self.body_height = 1.8
        self.hip_length = 1.4
        self.thigh_length = 3.0
        self.tibia_length = 3.2

        # Calculate ground offset
        self._calculate_ground_offset()

    def _calculate_ground_offset(self):
        """Calculate the Y offset needed to place the hexapod on the ground plane.

        This is calculated ONCE for the default standing pose and never changes.
        The robot can then move its legs freely and will naturally lift/tilt.
        """
        # Use the DEFAULT servo angles for ground calculation
        default_hip = 90
        default_thigh = 120
        default_tibia = 0

        min_y = float("inf")

        for leg_idx in range(6):
            _, foot_pos = self._calculate_leg_endpoints(
                leg_idx,
                default_hip,
                default_thigh,
                default_tibia,
            )
            if foot_pos[1] < min_y:
                min_y = foot_pos[1]

        # Ground plane is at y = -3.0
        # In default pose, feet should just barely touch the ground
        # Add a small offset so feet are slightly embedded (looks better)
        self.ground_offset = -3.0 - min_y + 0.2
        print(f"Ground offset calculated: {self.ground_offset:.2f} (min_y={min_y:.2f})")

    def _calculate_leg_endpoints(self, leg_idx, hip_angle, thigh_angle, tibia_angle):
        """Calculate the 3D positions of leg joints given servo angles.

        Servo angle definitions:
        - Hip: 90° is neutral (straight out), angles rotate left-right
        - Thigh: 0° points straight down, 180° points straight up
        - Tibia: 0° is perpendicular down from thigh, 180° is perpendicular up from thigh
        """
        leg_base_angle = leg_idx * 60  # Degrees around body

        # Convert to radians
        leg_rad = math.radians(leg_base_angle)
        hip_rad = math.radians(hip_angle - 90)  # Offset so 90° is neutral

        # Thigh: 0° = down (-90° in math), 180° = up (+90° in math)
        # So thigh_angle maps: 0→-90, 90→0, 180→+90
        thigh_math_angle = thigh_angle - 90
        thigh_rad = math.radians(thigh_math_angle)

        # Tibia: 0° = perpendicular down from thigh, 180° = perpendicular up
        # This is relative to the thigh, so 0° adds -90° to thigh angle
        tibia_math_angle = tibia_angle - 90
        tibia_rad = math.radians(tibia_math_angle)

        # Starting position at body vertex
        start_x = self.body_radius * math.cos(leg_rad)
        start_z = self.body_radius * math.sin(leg_rad)
        start_y = 0

        # Rotate to leg's coordinate frame
        cos_leg = math.cos(leg_rad)
        sin_leg = math.sin(leg_rad)

        # Hip servo + joint (0.3 + 0.8 + 0.5 sphere = 1.6 units out)
        hip_servo_extend = 1.6

        # Hip extends outward from body with rotation
        hip_base_x = start_x + cos_leg * hip_servo_extend
        hip_base_z = start_z + sin_leg * hip_servo_extend
        hip_base_y = start_y

        # Hip rotation affects the direction of the hip link
        hip_link_x = self.hip_length * math.cos(hip_rad)
        hip_link_y = self.hip_length * math.sin(hip_rad)

        # Hip joint is at the end of the hip servo
        hip_x = hip_base_x + cos_leg * hip_link_x
        hip_z = hip_base_z + sin_leg * hip_link_x
        hip_y = hip_base_y + hip_link_y

        # Thigh extends from hip joint
        # Account for both the hip rotation plane and thigh angle
        thigh_local_x = self.thigh_length * math.cos(hip_rad) * math.cos(thigh_rad)
        thigh_local_z = self.thigh_length * math.sin(hip_rad) * math.cos(thigh_rad)
        thigh_local_y = self.thigh_length * math.sin(thigh_rad)

        thigh_x = hip_x + thigh_local_x
        thigh_z = hip_z + thigh_local_z
        thigh_y = hip_y + thigh_local_y

        # Tibia continues from thigh
        # Combined angle of thigh + tibia (both relative to horizontal)
        combined_angle_rad = thigh_rad + tibia_rad

        tibia_local_x = (
            self.tibia_length * math.cos(hip_rad) * math.cos(combined_angle_rad)
        )
        tibia_local_z = (
            self.tibia_length * math.sin(hip_rad) * math.cos(combined_angle_rad)
        )
        tibia_local_y = self.tibia_length * math.sin(combined_angle_rad)

        foot_x = thigh_x + tibia_local_x
        foot_z = thigh_z + tibia_local_z
        foot_y = thigh_y + tibia_local_y

        hip_pos = np.array([hip_x, hip_y, hip_z])
        thigh_pos = np.array([thigh_x, thigh_y, thigh_z])
        foot_pos = np.array([foot_x, foot_y, foot_z])

        return (hip_pos, thigh_pos, foot_pos), foot_pos

    def _calculate_body_tilt(self):
        """Calculate body tilt based on foot positions.

        DISABLED: For now, keep the body level and let the legs do all the work.
        The robot will naturally appear tilted when some legs are shorter.
        """
        # No tilt - body stays perfectly level
        # The visual tilt comes naturally from leg positions
        return 0, 0, 0

    def initializeGL(self) -> None:
        """Initialize OpenGL."""
        glClearColor(0.06, 0.06, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)

        # Clean lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [8.0, 12.0, 8.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.45, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])

        glLightfv(GL_LIGHT1, GL_POSITION, [-6.0, 8.0, -6.0, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.2, 0.2, 0.25, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.6, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])

    def resizeGL(self, w: int, h: int) -> None:
        """Handle resize."""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h > 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self) -> None:
        """Paint OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0.0, -1.5, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        self._draw_ground_plane()

        # Apply ground offset only - no dynamic tilting
        glPushMatrix()
        glTranslatef(0.0, self.ground_offset, 0.0)

        # Body stays level - natural tilt comes from leg positions
        self._draw_hexapod()
        glPopMatrix()

    def _draw_ground_plane(self) -> None:
        """Draw simple ground plane."""
        glDisable(GL_LIGHTING)

        grid_size = 24
        grid_spacing = 2.0

        # Center lines
        glLineWidth(2.0)
        glColor4f(0.25, 0.3, 0.35, 0.6)
        glBegin(GL_LINES)
        glVertex3f(-grid_size * grid_spacing / 2, -3.0, 0)
        glVertex3f(grid_size * grid_spacing / 2, -3.0, 0)
        glVertex3f(0, -3.0, -grid_size * grid_spacing / 2)
        glVertex3f(0, -3.0, grid_size * grid_spacing / 2)
        glEnd()

        # Regular grid
        glLineWidth(1.0)
        glColor4f(0.15, 0.15, 0.22, 0.35)
        glBegin(GL_LINES)
        for i in range(-grid_size // 2, grid_size // 2 + 1):
            if i == 0:
                continue
            x = i * grid_spacing
            glVertex3f(-grid_size * grid_spacing / 2, -3.0, x)
            glVertex3f(grid_size * grid_spacing / 2, -3.0, x)
            glVertex3f(x, -3.0, -grid_size * grid_spacing / 2)
            glVertex3f(x, -3.0, grid_size * grid_spacing / 2)
        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def _draw_hexapod(self) -> None:
        """Draw hexapod robot with current servo positions."""
        self._draw_chassis()

        # Draw all 6 legs with their current servo angles
        for leg_idx in range(6):
            leg_angle = leg_idx * 60
            glPushMatrix()
            glRotatef(leg_angle, 0.0, 1.0, 0.0)
            self._draw_leg(
                leg_idx,
                self.servo_angles[leg_idx, 0],  # Hip
                self.servo_angles[leg_idx, 1],  # Thigh
                self.servo_angles[leg_idx, 2],  # Tibia
            )
            glPopMatrix()

    def _draw_chassis(self) -> None:
        """Draw proper hexagonal chassis with concave sides - FIXED."""
        # Black chassis material
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.08, 0.08, 0.08, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.15, 0.15, 0.15, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 60.0)
        glColor3f(0.12, 0.12, 0.12)

        body_radius = self.body_radius
        body_height = self.body_height
        curve_depth = 0.8
        curve_segments = 24

        # Generate all points for the hexagon with concave sides
        all_points = []
        for i in range(6):
            angle1 = i * 60 * math.pi / 180
            angle2 = (i + 1) * 60 * math.pi / 180

            # Vertices
            x1 = body_radius * math.cos(angle1)
            z1 = body_radius * math.sin(angle1)
            x2 = body_radius * math.cos(angle2)
            z2 = body_radius * math.sin(angle2)

            # Control point for concave curve
            mid_angle = (angle1 + angle2) / 2
            mid_x = (body_radius - curve_depth) * math.cos(mid_angle)
            mid_z = (body_radius - curve_depth) * math.sin(mid_angle)

            # Generate curve points
            for j in range(curve_segments):
                t = j / curve_segments
                x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mid_x + t**2 * x2
                z = (1 - t) ** 2 * z1 + 2 * (1 - t) * t * mid_z + t**2 * z2
                all_points.append((x, z))

        num_points = len(all_points)

        # Draw top surface
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, body_height / 2, 0.0)
        for x, z in all_points:
            glVertex3f(x, body_height / 2, z)
        # Close the loop
        glVertex3f(all_points[0][0], body_height / 2, all_points[0][1])
        glEnd()

        # Draw bottom surface
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(0.0, -body_height / 2, 0.0)
        for x, z in reversed(all_points):
            glVertex3f(x, -body_height / 2, z)
        # Close the loop
        glVertex3f(all_points[-1][0], -body_height / 2, all_points[-1][1])
        glEnd()

        # Draw side surface - PROPERLY CLOSED
        glBegin(GL_QUAD_STRIP)
        for i in range(num_points + 1):  # +1 to close the loop
            idx = i % num_points
            x, z = all_points[idx]

            # Calculate normal
            prev_idx = (idx - 1) % num_points
            next_idx = (idx + 1) % num_points

            prev_x, prev_z = all_points[prev_idx]
            next_x, next_z = all_points[next_idx]

            tx = next_x - prev_x
            tz = next_z - prev_z

            nx = -tz
            nz = tx
            length = math.sqrt(nx**2 + nz**2)
            if length > 0:
                nx /= length
                nz /= length

            glNormal3f(nx, 0.0, nz)
            glVertex3f(x, body_height / 2, z)
            glVertex3f(x, -body_height / 2, z)
        glEnd()

    def _draw_leg(
        self, leg_idx: int, hip_angle: float, thigh_angle: float, tibia_angle: float
    ) -> None:
        """
        Draw leg with servo-controlled joints.
        Hip: 40-150° (default 90°) - left-right rotation
        Thigh: 0-180° (default 120°) - 0° points down, 180° points up
        Tibia: 0-180° (default 0°) - 0° perpendicular down from thigh, 180° perpendicular up
        """

        # Yellow material for links
        def set_yellow_material():
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.35, 0.3, 0.0, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 0.9, 0.15, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.8, 0.8, 0.4, 1.0])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 70.0)

        # Black material for servos
        def set_black_material():
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.12, 0.12, 0.12, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.4, 0.4, 0.4, 1.0])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

        vertex_radius = self.body_radius
        glTranslatef(vertex_radius, 0.0, 0.0)

        glPushMatrix()

        # === HIP SERVO (black, allows left-right rotation) ===
        set_black_material()
        glColor3f(0.12, 0.12, 0.12)
        glTranslatef(0.3, 0.0, 0.0)
        self._draw_cylinder(0.0, 0.0, 0.0, 0.6, 0.8, axis="x")

        # Hip joint sphere
        glTranslatef(0.8, 0.0, 0.0)
        self._draw_sphere(0.5)

        # Apply hip rotation (offset by 90 for neutral position)
        glRotatef(hip_angle - 90, 0.0, 1.0, 0.0)

        # === HIP LINK (yellow) ===
        set_yellow_material()
        glColor3f(1.0, 0.9, 0.15)
        # Start right after hip joint sphere
        glTranslatef(0.5, 0.0, 0.0)
        self._draw_cylinder(0.0, 0.0, 0.0, 0.45, self.hip_length, axis="x")

        # === THIGH SERVO (black, allows up-down rotation) ===
        # Move to end of hip link
        glTranslatef(self.hip_length, 0.0, 0.0)
        set_black_material()
        glColor3f(0.12, 0.12, 0.12)

        # Thigh joint sphere
        self._draw_sphere(0.55)

        # Apply thigh rotation: 0° down, 180° up
        # In OpenGL: 0° servo = -90° rotation (pointing down)
        #            90° servo = 0° rotation (horizontal)
        #            180° servo = +90° rotation (pointing up)
        glRotatef(thigh_angle - 90, 0.0, 0.0, 1.0)

        # === THIGH LINK (yellow, fat part) ===
        set_yellow_material()
        glColor3f(1.0, 0.9, 0.15)
        # Start right after thigh joint sphere
        glTranslatef(0.6, 0.0, 0.0)
        self._draw_cylinder(0.0, 0.0, 0.0, 0.65, self.thigh_length, axis="x")

        # === KNEE SERVO (black) ===
        glTranslatef(self.thigh_length, 0.0, 0.0)
        set_black_material()
        glColor3f(0.12, 0.12, 0.12)

        # Knee joint sphere
        self._draw_sphere(0.6)

        # Apply tibia rotation: 0° perpendicular down from thigh, 180° perpendicular up
        # Same mapping as thigh
        glRotatef(tibia_angle - 90, 0.0, 0.0, 1.0)

        # === TIBIA (yellow, curved trunk-like) ===
        set_yellow_material()
        glColor3f(1.0, 0.9, 0.15)
        glTranslatef(0.6, 0.0, 0.0)
        self._draw_curved_tibia(self.tibia_length, 0.55, 0.35)

        glPopMatrix()

    def _draw_sphere(self, radius: float) -> None:
        """Draw a simple smooth sphere."""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, radius, 20, 20)
        gluDeleteQuadric(quadric)

    def _draw_cylinder(
        self,
        x: float,
        y: float,
        z: float,
        radius: float,
        length: float,
        axis: str = "x",
    ) -> None:
        """Draw a simple cylinder."""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        glPushMatrix()
        glTranslatef(x, y, z)

        if axis == "x":
            glRotatef(90, 0, 1, 0)
        elif axis == "y":
            glRotatef(-90, 1, 0, 0)

        gluCylinder(quadric, radius, radius, length, 20, 1)

        # Caps
        gluDisk(quadric, 0, radius, 20, 1)
        glTranslatef(0, 0, length)
        gluDisk(quadric, 0, radius, 20, 1)

        glPopMatrix()
        gluDeleteQuadric(quadric)

    def _draw_curved_tibia(
        self, length: float, radius_start: float, radius_end: float
    ) -> None:
        """Draw elegant curved tibia like a trunk."""
        segments = 30
        curve_angle = 25  # degrees of curve

        glPushMatrix()

        for i in range(segments):
            t = i / segments
            t_next = (i + 1) / segments

            # Position along curve
            x = length * t
            x_next = length * t_next

            # Downward curve
            y = -length * t * math.sin(curve_angle * math.pi / 180) * 0.4
            y_next = -length * t_next * math.sin(curve_angle * math.pi / 180) * 0.4

            # Radius taper
            r = radius_start + (radius_end - radius_start) * t
            r_next = radius_start + (radius_end - radius_start) * t_next

            # Draw segment
            glPushMatrix()
            glTranslatef(x, y, 0)

            # Calculate rotation for smooth curve
            dx = x_next - x
            dy = y_next - y
            angle = math.atan2(dy, dx) * 180 / math.pi

            glRotatef(angle, 0, 0, 1)

            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)

            segment_length = math.sqrt(dx**2 + dy**2)
            glRotatef(90, 0, 1, 0)
            gluCylinder(quadric, r, r_next, segment_length, 20, 1)

            gluDeleteQuadric(quadric)
            glPopMatrix()

        glPopMatrix()

    def set_servo_angle(self, leg: int, joint: int, angle: float) -> None:
        """Set servo angle for a specific leg and joint."""
        if 0 <= leg < 6 and 0 <= joint < 3:
            # Clamp angle to limits
            joint_names = ["hip", "thigh", "tibia"]
            min_ang, max_ang, _ = self.servo_limits[joint_names[joint]]
            angle = max(min_ang, min(max_ang, angle))

            self.servo_angles[leg, joint] = angle
            # DON'T recalculate ground offset - let the robot move naturally
            self.update()

    def get_servo_angle(self, leg: int, joint: int) -> float:
        """Get servo angle for a specific leg and joint."""
        if 0 <= leg < 6 and 0 <= joint < 3:
            return self.servo_angles[leg, joint]
        return 0.0

    def mousePressEvent(self, event) -> None:
        """Handle mouse press."""
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move."""
        if self.last_pos is not None:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()

            if event.buttons() & Qt.LeftButton:
                self.rotation_y += dx * 0.5
                self.rotation_x += dy * 0.5
                self.rotation_x = max(-89, min(89, self.rotation_x))
                self.update()

            self.last_pos = event.pos()

    def wheelEvent(self, event) -> None:
        """Handle mouse wheel."""
        delta = event.angleDelta().y()
        self.zoom += delta / 60.0
        self.zoom = max(-60, min(-10, self.zoom))
        self.update()


class PoseVisualizer(QWidget):
    """Pose visualizer widget that integrates with ServoMatrix."""

    servo_angle_changed = pyqtSignal(int, int, float)  # leg, joint, angle

    def __init__(self, parent=None):
        """Initialize pose visualizer."""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("3D Pose Visualization")
        title.setStyleSheet(
            """
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1a1a1a);
                color: #ffd700;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
                border: 1px solid #404040;
                border-bottom: 3px solid #ffd700;
            }
        """
        )

        self.gl_widget = PoseVisualizerGL()
        self.gl_widget.setMinimumSize(600, 600)
        self.gl_widget.setStyleSheet(
            """
            QOpenGLWidget {
                border: 1px solid #404040;
                background-color: #060608;
            }
        """
        )

        layout.addWidget(title)
        layout.addWidget(self.gl_widget, 1)

        self.setLayout(layout)

    def set_servo_angle(self, leg: int, joint: int, angle: float) -> None:
        """Set servo angle (called from ServoMatrix)."""
        self.gl_widget.set_servo_angle(leg, joint, angle)

    def get_servo_angle(self, leg: int, joint: int) -> float:
        """Get servo angle."""
        return self.gl_widget.get_servo_angle(leg, joint)

    def connect_to_servo_matrix(self, servo_matrix) -> None:
        """Connect this visualizer to a ServoMatrix widget."""
        # Store reference to servo matrix
        self._servo_matrix = servo_matrix

        # Connect each servo control to update the visualizer
        for limb_idx in range(6):
            for joint_idx in range(3):
                servo_idx = limb_idx + joint_idx * 6
                if servo_idx < len(servo_matrix._servo_controls):
                    servo = servo_matrix._servo_controls[servo_idx]

                    # Use a proper lambda that captures the current values
                    def make_handler(l, j):
                        return lambda angle: self.set_servo_angle(l, j, angle)

                    servo.angle_changed.connect(make_handler(limb_idx, joint_idx))

        # Initialize visualizer with current servo positions
        for limb_idx in range(6):
            for joint_idx in range(3):
                angle = servo_matrix.get_servo_angle(limb_idx, joint_idx)
                self.set_servo_angle(limb_idx, joint_idx, angle)
