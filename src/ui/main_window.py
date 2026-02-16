"""Main window for SIRA Console."""

from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QMenuBar,
    QMenu,
    QLabel,
    QAction,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from src.ui.tabs import (
    DashboardTab,
    ControlTab,
    AnalysisTab,
    ConnectionTab,
    DiagnosticsTab,
)
from src.ui.components import SignalIndicator, CustomStatusBar
from src.ui.styles import get_main_stylesheet
from src.core.config_loader import ConfigLoader
from src.utils.constants import ConnectionStatus, MovementStatus, TabIndex, Colors
from src.network import SocketClient  # NEW IMPORT


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: ConfigLoader):
        """
        Initialize main window.

        Args:
            config: Configuration loader
        """
        super().__init__()
        self.config = config

        # Create socket client (SINGLE INSTANCE for entire app)
        self.socket_client = SocketClient()

        self._setup_window()
        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()
        self._setup_timers()

    def _setup_window(self) -> None:
        """Setup window properties."""
        self.setWindowTitle(
            self.config.get_setting("window", "title", default="SIRA Console")
        )

        min_width = self.config.get_setting("window", "min_width", default=1280)
        min_height = self.config.get_setting("window", "min_height", default=720)
        default_width = self.config.get_setting("window", "default_width", default=1920)
        default_height = self.config.get_setting(
            "window", "default_height", default=1080
        )

        self.setMinimumSize(min_width, min_height)
        self.resize(default_width, default_height)

        # Apply stylesheet
        self.setStyleSheet(get_main_stylesheet())

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        # Create tabs - PASS socket_client to tabs that need it
        self.dashboard_tab = DashboardTab(socket_client=self.socket_client)
        self.control_tab = ControlTab(self.config)
        self.analysis_tab = AnalysisTab(socket_client=self.socket_client)
        self.connection_tab = ConnectionTab(socket_client=self.socket_client)
        self.diagnostics_tab = DiagnosticsTab()

        # Add tabs
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.control_tab, "Control")
        self.tab_widget.addTab(self.analysis_tab, "Analysis")
        self.tab_widget.addTab(self.connection_tab, "Connection")
        self.tab_widget.addTab(self.diagnostics_tab, "Diagnostics")

        self.setCentralWidget(self.tab_widget)

        # Create status bar
        self.status_bar = CustomStatusBar()
        self.setStatusBar(self.status_bar)

        # Create signal indicator (top right)
        self.signal_indicator = SignalIndicator()

        # Connect socket client to signal indicator
        self.socket_client.connection_changed.connect(self._on_connection_changed)

    def _setup_menu(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()

        robot_label = QLabel("SIRA Console")
        robot_label.setObjectName("RobotNameLabel")
        robot_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        menubar.setCornerWidget(robot_label, Qt.TopLeftCorner)
        # # Options menu
        # options_menu = menubar.addMenu("Options")

        # # Exit action
        # exit_action = QAction("Exit", self)
        # exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        # # exit_action.triggered.connect(self._confirm_exit)
        # exit_action.triggered.connect(self.close)

        # options_menu.addAction(exit_action)

        # Add signal indicator to menu bar (right side)
        menubar.setCornerWidget(self.signal_indicator, Qt.TopRightCorner)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Tab switching shortcuts
        for i in range(1, 6):
            shortcut = QKeySequence(f"Ctrl+{i}")
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda checked, idx=i - 1: self._switch_tab(idx))
            self.addAction(action)

        # Test mode toggle (Ctrl+T) - only works in Control tab
        test_action = QAction(self)
        test_action.setShortcut(QKeySequence("Ctrl+T"))
        test_action.triggered.connect(self._toggle_test_mode)
        self.addAction(test_action)

        # Record toggle (Ctrl+R) - only works in Dashboard tab
        record_action = QAction(self)
        record_action.setShortcut(QKeySequence("Ctrl+R"))
        record_action.triggered.connect(self._toggle_recording)
        self.addAction(record_action)

    def _setup_timers(self) -> None:
        """Setup periodic timers."""
        # Update status indicators
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(100)  # 10 Hz update

    def _switch_tab(self, index: int) -> None:
        """
        Switch to a specific tab.

        Args:
            index: Tab index
        """
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)

    def _toggle_test_mode(self) -> None:
        """Toggle test mode in control tab."""
        if self.tab_widget.currentIndex() == TabIndex.CONTROL:
            current_state = self.control_tab.test_switch.isChecked()
            self.control_tab.test_switch.setChecked(not current_state)

    def _toggle_recording(self) -> None:
        """Toggle recording in dashboard tab."""
        if self.tab_widget.currentIndex() == TabIndex.DASHBOARD:
            camera = self.dashboard_tab.camera_view
            camera.record_btn.setChecked(not camera.record_btn.isChecked())
            camera._toggle_recording(camera.record_btn.isChecked())

    def _update_status(self) -> None:
        """Update status indicators."""
        # This would be connected to actual robot state in production
        pass

    def _on_connection_changed(self, connected: bool) -> None:
        """
        Handle connection state change.

        Args:
            connected: Connection state
        """
        if connected:
            self.set_connection_status(ConnectionStatus.CONNECTED)
        else:
            self.set_connection_status(ConnectionStatus.DISCONNECTED)

    def _confirm_exit(self) -> bool:
        """Show exit confirmation dialog."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit SIRA Console?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        return reply == QMessageBox.Yes

    def set_connection_status(self, status: ConnectionStatus) -> None:
        """
        Set connection status.

        Args:
            status: Connection status
        """
        self.signal_indicator.set_status(status)

    def set_movement_status(self, status: MovementStatus) -> None:
        """
        Set movement status.

        Args:
            status: Movement status
        """
        self.status_bar.set_movement_status(status)

    def closeEvent(self, event) -> None:
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Disconnect socket client before closing
        if self.socket_client.is_connected():
            self.socket_client.disconnect()

        # Override to prevent direct closing without confirmation
        if self._confirm_exit():
            event.accept()
        else:
            event.ignore()
