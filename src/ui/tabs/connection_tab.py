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
)
from PyQt5.QtCore import Qt, pyqtSlot
from src.utils.constants import Colors
from src.network import SocketClient

IP = "192.168.0.109"


class ConnectionTab(QWidget):
    """Connection tab for managing robot connections."""

    def __init__(self, socket_client: SocketClient, parent=None):
        """
        Initialize connection tab.

        Args:
            socket_client: Shared socket client instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.socket_client = socket_client
        self._connected = False

        # Connect to socket client signals
        self.socket_client.connection_changed.connect(self._on_connection_changed)
        self.socket_client.error_occurred.connect(self._on_error)

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
        self.protocol_combo.addItems(
            ["TCP Socket", "Serial (Not Implemented)", "UDP (Not Implemented)"]
        )
        self.protocol_combo.currentTextChanged.connect(self._on_protocol_changed)

        settings_layout.addWidget(protocol_label, 0, 0)
        settings_layout.addWidget(self.protocol_combo, 0, 1)

        # Preset configurations
        preset_label = QLabel("Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Custom", f"Pi Hotspot ({IP})", "Local Network"])
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)

        settings_layout.addWidget(preset_label, 1, 0)
        settings_layout.addWidget(self.preset_combo, 1, 1)

        # TCP settings
        host_label = QLabel("Host (IP):")
        self.host_input = QLineEdit(IP)
        self.host_input.setPlaceholderText(f"e.g., {IP}")

        port_label = QLabel("Port:")
        self.port_input = QLineEdit("8080")
        self.port_input.setPlaceholderText("e.g., 8080")

        settings_layout.addWidget(host_label, 2, 0)
        settings_layout.addWidget(self.host_input, 2, 1)
        settings_layout.addWidget(port_label, 3, 0)
        settings_layout.addWidget(self.port_input, 3, 1)

        settings_group.setLayout(settings_layout)

        # Connection control buttons
        button_layout = QHBoxLayout()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._toggle_connection)
        self.connect_btn.setMinimumHeight(40)

        button_layout.addWidget(self.connect_btn)
        button_layout.addStretch()

        # Connection status group
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {Colors.PRIMARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                font-family: Consolas, Monaco, 'Courier New', monospace;
                font-size: 9pt;
            }}
        """
        )
        self.status_text.append("Ready to connect...")
        self.status_text.append("\nQuick Setup:")
        self.status_text.append("1. Switch On the Hexapod")
        self.status_text.append("2. Select 'Pi Hotspot' preset or enter Pi's IP")
        self.status_text.append("3. Click 'Connect'")

        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)

        # Protocol info group
        info_group = QGroupBox("Protocol Information")
        info_layout = QVBoxLayout()

        self.info_label = QLabel(
            "<b>TCP Socket Protocol:</b><br>"
            "Direct socket connection for real-time camera streaming and telemetry.<br>"
            "Low latency, high bandwidth, reliable delivery.<br><br>"
            f"<b>Pi Hotspot Mode:</b> Pi at {IP} (always)<br>"
            "<b>Local Network:</b> Find Pi's IP with 'hostname -I' command on Pi"
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
        if protocol == "TCP Socket":
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.preset_combo.setEnabled(True)
        else:
            self.status_text.append(f"\n{protocol} not yet implemented")

    def _on_preset_changed(self, preset: str) -> None:
        """
        Handle preset change.

        Args:
            preset: Selected preset
        """
        if preset == f"Pi Hotspot {IP}":
            self.host_input.setText(IP)
            self.port_input.setText("8080")
            self.status_text.append("\nPreset: Pi Hotspot mode selected")
        elif preset == "Local Network":
            self.host_input.setText("192.168.1.100")
            self.port_input.setText("8080")
            self.status_text.append("\nPreset: Local network - update IP if needed")
        # Custom = no change

    def _toggle_connection(self) -> None:
        """Toggle connection state."""
        if not self._connected:
            # Attempt connection
            protocol = self.protocol_combo.currentText()

            if protocol != "TCP Socket":
                self.status_text.append(f"\n{protocol} not implemented yet")
                return

            # Get connection parameters
            host = self.host_input.text().strip()
            try:
                port = int(self.port_input.text().strip())
            except ValueError:
                self.status_text.append("\nError: Invalid port number")
                return

            if not host:
                self.status_text.append("\nError: Please enter host IP")
                return

            self.status_text.append(f"\nConnecting to {host}:{port}...")
            self.connect_btn.setEnabled(False)

            # Attempt connection
            success = self.socket_client.connect(host, port)

            self.connect_btn.setEnabled(True)

            if not success:
                self.status_text.append("Connection failed - see error above")
        else:
            # Disconnect
            self.socket_client.disconnect()

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool):
        """
        Handle connection state change.

        Args:
            connected: New connection state
        """
        self._connected = connected

        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {Colors.STATUS_RED};
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                }}
            """
            )
            self.status_text.append("Connected successfully!")
            self.host_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.preset_combo.setEnabled(False)
            self.protocol_combo.setEnabled(False)
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("")
            self.status_text.append("Disconnected")
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.preset_combo.setEnabled(True)
            self.protocol_combo.setEnabled(True)

    @pyqtSlot(str)
    def _on_error(self, error_msg: str):
        """
        Handle connection error.

        Args:
            error_msg: Error message
        """
        self.status_text.append(f"\nError: {error_msg}")
