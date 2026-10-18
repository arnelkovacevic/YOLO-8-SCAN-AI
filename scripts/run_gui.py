"""Wrapper to start the PyQt GUI from the repository root.

This imports the existing `app_pyqt.py` class `YOLOApp` and runs it.
Keep this small so users can run `python scripts/run_gui.py`.
"""
import os
import sys

# Ensure repository root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PyQt5.QtWidgets import QApplication
from app_pyqt import YOLOApp


def main():
    app = QApplication(sys.argv)
    window = YOLOApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
