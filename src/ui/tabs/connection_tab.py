"""Connection tab for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QTextEdit,
    QFrame,
)
from PyQt5.QtCore import Qt
from src.utils.constants import Colors


class ConnectionTab(QWidget):
    """Connection tab for managing robot connections."""

    def __init__(self, parent=None):
        """
        Initialize connection tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._connected = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Connection settings group
        settings_group = QGroupBox("Connection Settings")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(12)

        # Protocol selection
        protocol_label = QLabel("Protocol:")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["Serial", "TCP", "UDP", "WebSocket"])
        self.protocol_combo.currentTextChanged.connect(self._on_protocol_changed)

        settings_layout.addWidget(protocol_label, 0, 0)
        settings_layout.addWidget(self.protocol_combo, 0, 1)

        # Serial settings (shown by default)
        self.serial_widget = QWidget()
        serial_layout = QGridLayout(self.serial_widget)

        port_label = QLabel("Port:")
        self.port_combo = QComboBox()
        self.port_combo.addItems(
            ["COM1", "COM2", "COM3", "/dev/ttyUSB0", "/dev/ttyUSB1"]
        )
        self.port_combo.setEditable(True)

        baud_label = QLabel("Baud Rate:")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("115200")

        serial_layout.addWidget(port_label, 0, 0)
        serial_layout.addWidget(self.port_combo, 0, 1)
        serial_layout.addWidget(baud_label, 1, 0)
        serial_layout.addWidget(self.baud_combo, 1, 1)

        # TCP/UDP settings (hidden by default)
        self.network_widget = QWidget()
        network_layout = QGridLayout(self.network_widget)

        host_label = QLabel("Host:")
        self.host_input = QLineEdit("192.168.1.100")

        port_label = QLabel("Port:")
        self.port_input = QLineEdit("8080")

        network_layout.addWidget(host_label, 0, 0)
        network_layout.addWidget(self.host_input, 0, 1)
        network_layout.addWidget(port_label, 1, 0)
        network_layout.addWidget(self.port_input, 1, 1)

        self.network_widget.hide()

        settings_layout.addWidget(self.serial_widget, 1, 0, 1, 2)
        settings_layout.addWidget(self.network_widget, 1, 0, 1, 2)

        settings_group.setLayout(settings_layout)

        # Connection control buttons
        button_layout = QHBoxLayout()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._toggle_connection)

        self.refresh_btn = QPushButton("Refresh Ports")
        self.refresh_btn.clicked.connect(self._refresh_ports)

        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()

        # Connection status group
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {Colors.PRIMARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                font-family: Consolas, Monaco, Courier New, monospace;
                font-size: 9pt;
            }}
        """
        )
        self.status_text.append("Ready to connect...")

        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)

        # Protocol info group
        info_group = QGroupBox("Protocol Information")
        info_layout = QVBoxLayout()

        self.info_label = QLabel(
            "<b>Serial Protocol:</b><br>"
            "Direct serial connection via USB or UART.<br>"
            "Suitable for local connections with reliable data transfer.<br><br>"
            "<b>Configuration:</b> Select the appropriate COM port and baud rate."
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)

        # Add all groups to main layout
        layout.addWidget(settings_group)
        layout.addLayout(button_layout)
        layout.addWidget(status_group)
        layout.addWidget(info_group)
        layout.addStretch()

        self.setLayout(layout)

    def _on_protocol_changed(self, protocol: str) -> None:
        """
        Handle protocol change.

        Args:
            protocol: Selected protocol
        """
        if protocol == "Serial":
            self.serial_widget.show()
            self.network_widget.hide()
            self.info_label.setText(
                "<b>Serial Protocol:</b><br>"
                "Direct serial connection via USB or UART.<br>"
                "Suitable for local connections with reliable data transfer.<br><br>"
                "<b>Configuration:</b> Select the appropriate COM port and baud rate."
            )
        else:
            self.serial_widget.hide()
            self.network_widget.show()
            if protocol == "TCP":
                self.info_label.setText(
                    "<b>TCP Protocol:</b><br>"
                    "Reliable network connection with guaranteed delivery.<br>"
                    "Suitable for WiFi or Ethernet connections.<br><br>"
                    "<b>Configuration:</b> Enter the robot's IP address and port."
                )
            elif protocol == "UDP":
                self.info_label.setText(
                    "<b>UDP Protocol:</b><br>"
                    "Fast network connection with minimal overhead.<br>"
                    "Suitable for real-time control with occasional packet loss tolerance.<br><br>"
                    "<b>Configuration:</b> Enter the robot's IP address and port."
                )
            else:  # WebSocket
                self.info_label.setText(
                    "<b>WebSocket Protocol:</b><br>"
                    "Bidirectional network connection over HTTP/HTTPS.<br>"
                    "Suitable for cloud-based or web-integrated deployments.<br><br>"
                    "<b>Configuration:</b> Enter the WebSocket server address and port."
                )

    def _toggle_connection(self) -> None:
        """Toggle connection state."""
        if not self._connected:
            # Connect
            protocol = self.protocol_combo.currentText()
            self.status_text.append(f"\nAttempting to connect via {protocol}...")
            self.status_text.append("Connection successful!")
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {Colors.STATUS_RED};
                }}
            """
            )
            self._connected = True
        else:
            # Disconnect
            self.status_text.append("\nDisconnecting...")
            self.status_text.append("Disconnected.")
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("")
            self._connected = False

    def _refresh_ports(self) -> None:
        """Refresh available ports."""
        self.status_text.append("\nRefreshing available ports...")
        self.status_text.append("Found 3 available ports.")
