"""
SIRA Console - Spider Inspired Robotic Architecture Control Interface

Main entry point for the application.
"""

import sys
from src.core import Application


def main():
    """Main function."""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
