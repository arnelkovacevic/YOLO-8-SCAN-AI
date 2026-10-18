"""Download the large official YOLO weights that are too big for GitHub (>100 MB).

Usage:  python scripts/download_models.py
Files are saved into the models/ folder.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
LARGE_MODELS = ["yolov8x.pt", "yolov5x6u.pt"]


def main():
    from ultralytics.utils.downloads import attempt_download_asset

    MODELS_DIR.mkdir(exist_ok=True)
    for name in LARGE_MODELS:
        target = MODELS_DIR / name
        if target.exists():
            print(f"✔ {name} already present")
            continue
        print(f"⬇ downloading {name} ...")
        downloaded = Path(attempt_download_asset(name))
        if downloaded.exists() and downloaded.resolve() != target.resolve():
            shutil.move(str(downloaded), target)
        print(f"✔ saved to {target}")


if __name__ == "__main__":
    sys.exit(main())
