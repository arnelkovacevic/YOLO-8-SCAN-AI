"""Project paths, always relative to the project root (never absolute)."""
import sys
from pathlib import Path

# When frozen with PyInstaller the project root is the folder of the executable.
if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parents[3]

MODELS_DIR = ROOT / "models"
SAMPLES_DIR = ROOT / "assets" / "sample"
OUTPUT_DIR = ROOT / "output"   # screenshots and recordings
