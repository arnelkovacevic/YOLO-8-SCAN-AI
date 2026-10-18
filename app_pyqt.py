"""Backward-compatible launcher: `python app_pyqt.py` starts the same app as `python main.py`."""
from main import main

if __name__ == "__main__":
    main()
