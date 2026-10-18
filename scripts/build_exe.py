"""Build a standalone executable with PyInstaller.

Usage:  pip install -r requirements-dev.txt
        python scripts/build_exe.py
The executable is created in dist/. Copy the models/ and assets/ folders next to it.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--windowed", "--name", "SCAN_AI",
        "--paths", str(ROOT),
        "--collect-submodules", "ultralytics",
        str(ROOT / "main.py"),
    ]
    subprocess.check_call(cmd, cwd=ROOT)


if __name__ == "__main__":
    main()
