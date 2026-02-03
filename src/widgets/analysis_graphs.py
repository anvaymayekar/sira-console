"""Analysis graphs widget for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
from src.utils.constants import Colors
import numpy as np
from collections import deque
from datetime import datetime


class AnalysisGraphs(QWidget):
    """Analysis graphs widget with multiple visualization options."""

    def __init__(self, parent=None):
        """
        Initialize analysis graphs.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._data_history = {
            "battery": deque(maxlen=300),
            "temperature": deque(maxlen=300),
            "imu_x": deque(maxlen=300),
            "imu_y": deque(maxlen=300),
            "imu_z": deque(maxlen=300),
            "timestamps": deque(maxlen=300),
        }
        self._setup_ui()
        self._start_demo_data()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Control bar
        control_layout = QHBoxLayout()

        graph_label = QLabel("Graph Type:")
        graph_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        self.graph_combo = QComboBox()
        self.graph_combo.addItems(
            [
                "Battery Voltage",
                "Temperature",
                "IMU Orientation",
                "Movement Pattern",
                "Human Presence Log",
            ]
        )
        self.graph_combo.currentTextChanged.connect(self._change_graph)

        control_layout.addWidget(graph_label)
        control_layout.addWidget(self.graph_combo)
        control_layout.addStretch()

        # Graph container
        self.graph_container = QFrame()
        self.graph_container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.PRIMARY_BG};
                border: 1px solid {Colors.BORDER};
            }}
        """
        )

        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)

        # Setup PyQtGraph
        pg.setConfigOption("background", Colors.PRIMARY_BG)
        pg.setConfigOption("foreground", Colors.TEXT_PRIMARY)

        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(Colors.PRIMARY_BG)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel(
            "left", "Battery Voltage", units="V", color=Colors.TEXT_PRIMARY
        )
        self.plot_widget.setLabel(
            "bottom", "Time", units="s", color=Colors.TEXT_PRIMARY
        )

        self.curve = self.plot_widget.plot(pen=pg.mkPen(Colors.STATUS_GREEN, width=2))

        self.graph_layout.addWidget(self.plot_widget)

        # Human presence log (hidden by default)
        self.presence_log = QLabel("Human Presence Log\n\nNo detections recorded.")
        self.presence_log.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                background-color: {Colors.PANEL_BG};
                padding: 16px;
                border: 1px solid {Colors.BORDER};
            }}
        """
        )
        self.presence_log.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.presence_log.hide()

        self.graph_layout.addWidget(self.presence_log)

        layout.addLayout(control_layout)
        layout.addWidget(self.graph_container, 1)

        self.setLayout(layout)

    def _change_graph(self, graph_type: str) -> None:
        """
        Change displayed graph.

        Args:
            graph_type: Type of graph to display
        """
        if graph_type == "Human Presence Log":
            self.plot_widget.hide()
            self.presence_log.show()
        else:
            self.presence_log.hide()
            self.plot_widget.show()

            # Update labels and data
            if graph_type == "Battery Voltage":
                self.plot_widget.setLabel("left", "Battery Voltage", units="V")
                self._update_plot("battery", Colors.STATUS_GREEN)
            elif graph_type == "Temperature":
                self.plot_widget.setLabel("left", "Temperature", units="°C")
                self._update_plot("temperature", Colors.STATUS_RED)
            elif graph_type == "IMU Orientation":
                self.plot_widget.setLabel("left", "Orientation", units="°")
                self._update_plot_multi(["imu_x", "imu_y", "imu_z"])

    def _update_plot(self, data_key: str, color: str) -> None:
        """
        Update plot with single data series.

        Args:
            data_key: Key for data series
            color: Plot color
        """
        data = list(self._data_history[data_key])
        x = list(range(len(data)))
        self.curve.setData(x, data, pen=pg.mkPen(color, width=2))

    def _update_plot_multi(self, data_keys: list) -> None:
        """
        Update plot with multiple data series.

        Args:
            data_keys: List of data keys
        """
        self.plot_widget.clear()
        colors = [Colors.STATUS_GREEN, Colors.ACCENT_YELLOW, Colors.STATUS_RED]

        for i, key in enumerate(data_keys):
            data = list(self._data_history[key])
            x = list(range(len(data)))
            self.plot_widget.plot(
                x, data, pen=pg.mkPen(colors[i], width=2), name=key.upper()
            )

    def _start_demo_data(self) -> None:
        """Start generating demo data."""
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self._generate_demo_data)
        self.demo_timer.start(100)

    def _generate_demo_data(self) -> None:
        """Generate demo data for visualization."""
        # Generate random but realistic data
        if len(self._data_history["battery"]) == 0:
            battery = 12.0
            temp = 25.0
            imu_x = 0.0
            imu_y = 0.0
            imu_z = 0.0
        else:
            battery = self._data_history["battery"][-1] + np.random.uniform(-0.01, 0.01)
            temp = self._data_history["temperature"][-1] + np.random.uniform(-0.1, 0.1)
            imu_x = self._data_history["imu_x"][-1] + np.random.uniform(-1, 1)
            imu_y = self._data_history["imu_y"][-1] + np.random.uniform(-1, 1)
            imu_z = self._data_history["imu_z"][-1] + np.random.uniform(-1, 1)

        # Clamp values
        battery = np.clip(battery, 10.0, 13.0)
        temp = np.clip(temp, 20.0, 40.0)
        imu_x = np.clip(imu_x, -45.0, 45.0)
        imu_y = np.clip(imu_y, -45.0, 45.0)
        imu_z = np.clip(imu_z, -45.0, 45.0)

        # Add to history
        self._data_history["battery"].append(battery)
        self._data_history["temperature"].append(temp)
        self._data_history["imu_x"].append(imu_x)
        self._data_history["imu_y"].append(imu_y)
        self._data_history["imu_z"].append(imu_z)
        self._data_history["timestamps"].append(datetime.now())

        # Update current graph
        current_graph = self.graph_combo.currentText()
        if current_graph == "Battery Voltage":
            self._update_plot("battery", Colors.STATUS_GREEN)
        elif current_graph == "Temperature":
            self._update_plot("temperature", Colors.STATUS_RED)
        elif current_graph == "IMU Orientation":
            self._update_plot_multi(["imu_x", "imu_y", "imu_z"])
