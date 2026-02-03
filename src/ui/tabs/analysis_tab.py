"""Analysis tab for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.widgets import AnalysisGraphs


class AnalysisTab(QWidget):
    """Analysis tab containing graphs and visualizations."""

    def __init__(self, parent=None):
        """
        Initialize analysis tab.

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

        # Analysis graphs widget
        self.analysis_graphs = AnalysisGraphs()

        layout.addWidget(self.analysis_graphs)

        self.setLayout(layout)
