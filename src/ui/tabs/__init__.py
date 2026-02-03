"""Tabs package for SIRA Console."""

from .dashboard_tab import DashboardTab
from .control_tab import ControlTab
from .analysis_tab import AnalysisTab
from .connection_tab import ConnectionTab
from .diagnostics_tab import DiagnosticsTab

__all__ = [
    "DashboardTab",
    "ControlTab",
    "AnalysisTab",
    "ConnectionTab",
    "DiagnosticsTab",
]
