"""Stylesheet definitions for SIRA Console."""

from src.utils.constants import Colors, Fonts


def get_main_stylesheet() -> str:
    """
    Get main application stylesheet.

    Returns:
        QSS stylesheet string
    """
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {Colors.PRIMARY_BG};
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {Colors.BORDER};
        background-color: {Colors.PRIMARY_BG};
        top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_SECONDARY};
        padding: 10px 20px;
        margin-right: 2px;
        min-width: 100px;
        border: 1px solid {Colors.BORDER};
        border-bottom: none;
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    QTabBar::tab:selected {{
        background-color: {Colors.PRIMARY_BG};
        color: {Colors.TEXT_PRIMARY};
        border-bottom: 2px solid {Colors.ACCENT_YELLOW};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: #1f1f1f;
        color: {Colors.TEXT_PRIMARY};
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        border-bottom: 1px solid {Colors.BORDER};
        padding: 2px;
    }}
    
    QMenuBar::item {{
        padding: 6px 12px;
        background-color: transparent;
    }}
    
    QMenuBar::item:selected {{
        background-color: {Colors.PANEL_BG};
    }}
    
    QMenu {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
    }}
    
    QMenu::item {{
        padding: 6px 30px;
    }}
    
    QMenu::item:selected {{
        background-color: {Colors.PANEL_BG};
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 6px 16px;
        font-size: {Fonts.SIZE_NORMAL}pt;
        min-height: 24px;
    }}
    
    QPushButton:hover {{
        background-color: {Colors.PANEL_BG};
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}
    
    QPushButton:pressed {{
        background-color: {Colors.PRIMARY_BG};
    }}
    
    QPushButton:disabled {{
        background-color: {Colors.PRIMARY_BG};
        color: {Colors.TEXT_DISABLED};
        border: 1px solid {Colors.BORDER};
    }}
    
    /* Labels */
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
        background-color: transparent;
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    /* Line Edit */
    QLineEdit {{
        background-color: {Colors.PANEL_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 6px;
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    QLineEdit:focus {{
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}
    
    /* Combo Box */
    QComboBox {{
        background-color: {Colors.PANEL_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 6px;
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    QComboBox:hover {{
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        selection-background-color: {Colors.PANEL_BG};
        border: 1px solid {Colors.BORDER};
    }}
    
    /* Slider */
    QSlider::groove:horizontal {{
        background-color: {Colors.PANEL_BG};
        height: 6px;
        border: 1px solid {Colors.BORDER};
    }}
    
    QSlider::handle:horizontal {{
        background-color: {Colors.TEXT_PRIMARY};
        width: 14px;
        margin: -5px 0;
        border: 1px solid {Colors.BORDER};
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {Colors.ACCENT_YELLOW};
    }}
    
    /* Spin Box */
    QSpinBox, QDoubleSpinBox {{
        background-color: {Colors.PANEL_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 4px;
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}
    
    /* Text Edit */
    QTextEdit, QPlainTextEdit {{
        background-color: {Colors.PANEL_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        font-family: {Fonts.FAMILY};
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}

    /* Scroll Area */
    QScrollArea#HealthContainer {{
        border: 1px solid {Colors.BORDER};
        background-color: {Colors.PRIMARY_BG};
    }}

    QScrollArea::viewport, #HealthContainer {{
        background-color: {Colors.PRIMARY_BG};
    }}
    
    /* Scroll Bar */
    QScrollBar:vertical {{
        background-color: {Colors.PRIMARY_BG};
        width: 12px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {Colors.BORDER};
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {Colors.TEXT_SECONDARY};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {Colors.PRIMARY_BG};
        height: 12px;
        border: none;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {Colors.BORDER};
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {Colors.TEXT_SECONDARY};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Check Box */
    QCheckBox {{
        color: {Colors.TEXT_PRIMARY};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {Colors.BORDER};
        background-color: {Colors.PANEL_BG};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {Colors.ACCENT_YELLOW};
        border: 1px solid {Colors.ACCENT_YELLOW};
    }}
    
    QCheckBox::indicator:hover {{
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}
    
    /* Radio Button */
    QRadioButton {{
        color: {Colors.TEXT_PRIMARY};
        spacing: 8px;
    }}
    
    QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {Colors.BORDER};
        border-radius: 8px;
        background-color: {Colors.PANEL_BG};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {Colors.ACCENT_YELLOW};
        border: 1px solid {Colors.ACCENT_YELLOW};
    }}
    
    QRadioButton::indicator:hover {{
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}
    
    /* Group Box */
    QGroupBox {{
        border: 1px solid {Colors.BORDER};
        margin-top: 12px;
        padding-top: 12px;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        color: {Colors.TEXT_SECONDARY};
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {Colors.BORDER};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {Colors.TEXT_SECONDARY};
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        border-top: 1px solid {Colors.BORDER};
    }}
    
    /* Tool Tip */
    QToolTip {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 4px;
    }}
    
    /* Frame */
    QFrame {{
        border: none;
    }}

    /* Message Box */

    QMessageBox {{
        background-color: {Colors.SECONDARY_BG};
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
        font-size: {Fonts.SIZE_NORMAL}pt;
    }}

    QMessageBox QLabel {{
        color: {Colors.TEXT_PRIMARY};
        background-color: transparent;
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
        padding: 6px 16px;
        background-color: {Colors.PANEL_BG};
        border: 1px solid {Colors.BORDER};
        color: {Colors.TEXT_PRIMARY};
    }}

    QMessageBox QPushButton:hover {{
        background-color: {Colors.SECONDARY_BG};
        border: 1px solid {Colors.TEXT_SECONDARY};
    }}

    QMessageBox QPushButton:pressed {{
        background-color: {Colors.PRIMARY_BG};
    }}

    QMessageBox QPushButton:default {{
        border: 1px solid {Colors.ACCENT_YELLOW};
    }}

    QMessageBox QCheckBox {{
        color: {Colors.TEXT_PRIMARY};
    }}

    QLabel#RobotNameLabel {{
        font-size: 13pt;
        font-weight: 600;
        letter-spacing: 1px;
        color: #f5c542;
        padding-right: 12px;
    }}

    """


def get_status_indicator_style(color: str, size: int = 10) -> str:
    """
    Get status indicator stylesheet.

    Args:
        color: Status color
        size: Indicator size in pixels

    Returns:
        QSS stylesheet string
    """
    return f"""
    QLabel {{
        background-color: {color};
        border-radius: {size // 2}px;
        min-width: {size}px;
        max-width: {size}px;
        min-height: {size}px;
        max-height: {size}px;
    }}
    """
