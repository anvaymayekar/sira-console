"""Robot state model for SIRA Console."""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ServoState:
    """State of a single servo."""

    limb_index: int
    joint_index: int
    current_angle: float
    target_angle: float
    is_moving: bool = False


@dataclass
class SensorData:
    """Sensor data from the robot."""

    battery_voltage: float = 0.0
    battery_percentage: float = 0.0
    imu_x: float = 0.0
    imu_y: float = 0.0
    imu_z: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    altitude: float = 0.0
    front_distance: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RobotState:
    """Complete state of the robot."""

    connection_status: str = "Disconnected"
    movement_status: str = "Ready"
    servos: List[ServoState] = field(default_factory=list)
    sensor_data: SensorData = field(default_factory=SensorData)
    is_test_mode: bool = False

    def __post_init__(self):
        """Initialize servo states if empty."""
        if not self.servos:
            for limb in range(6):
                for joint in range(3):
                    self.servos.append(
                        ServoState(
                            limb_index=limb,
                            joint_index=joint,
                            current_angle=90.0 if joint == 0 else 0.0,
                            target_angle=90.0 if joint == 0 else 0.0,
                        )
                    )

    def get_servo(self, limb: int, joint: int) -> ServoState:
        """
        Get servo state by limb and joint index.

        Args:
            limb: Limb index (0-5)
            joint: Joint index (0-2)

        Returns:
            ServoState object
        """
        index = limb * 3 + joint
        return self.servos[index]

    def set_servo_angle(self, limb: int, joint: int, angle: float) -> None:
        """
        Set target angle for a servo.

        Args:
            limb: Limb index (0-5)
            joint: Joint index (0-2)
            angle: Target angle in degrees
        """
        servo = self.get_servo(limb, joint)
        servo.target_angle = angle
        servo.is_moving = abs(servo.current_angle - angle) > 0.5

    def update_sensor_data(self, data: Dict[str, Any]) -> None:
        """
        Update sensor data from dictionary.

        Args:
            data: Dictionary containing sensor values
        """
        for key, value in data.items():
            if hasattr(self.sensor_data, key):
                setattr(self.sensor_data, key, value)
        self.sensor_data.timestamp = datetime.now()
