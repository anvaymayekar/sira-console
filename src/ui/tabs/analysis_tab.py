"""Analysis tab for SIRA Console."""

from typing import Optional
from src.network import SocketClient
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.widgets import AnalysisGraphs


class AnalysisTab(QWidget):
    """Analysis tab containing graphs and visualizations."""

    def __init__(self, socket_client: Optional[SocketClient] = None, parent=None):
        """
        Initialize analysis tab.

        Args:
            socket_client: Socket client for data
            parent: Parent widget
        """
        super().__init__(parent)
        self.socket_client = socket_client
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Analysis graphs widget
        self.analysis_graphs = AnalysisGraphs(socket_client=self.socket_client)

        layout.addWidget(self.analysis_graphs)

        self.setLayout(layout)
