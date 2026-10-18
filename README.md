# YOLOv8 Object Detection with OpenCV and Ultralytics

This Python script uses YOLOv8 from Ultralytics for real-time object detection using OpenCV. The script initializes a camera, loads the YOLOv8 model, and processes frames from the camera, annotating detected objects with bounding boxes.

## Prerequisites

Make sure you have the following libraries installed:

- `cv2` (OpenCV)
# YOLO-8-SCAN_AI

Short description
-----------------
YOLO-8-SCAN_AI is a small toolkit that uses Ultralytics YOLO models for real-time object detection. The repository contains several example scripts (webcam inference, GUI using PyQt), ROS node examples, and model weights (stored locally).

What this project provides
-------------------------
- Real-time webcam inference examples (`webcam.py`, `scripts/run_webcam.py`).
- A PyQt5 GUI for live detection (`app_pyqt.py`, runnable with `scripts/run_gui.py`).
- Utility helpers under `src/yolo_scan` to centralize model loading and per-frame inference.
- Example ROS1/ROS2 node files (`ROS1_node.py`, `ROS2_node.py`) — these are example stubs and may require adjustment for your ROS topics.

Models included (short summary)
------------------------------
The repository contains several `.pt` files (model weights). See `models/` for your local copies. A brief summary (from `setting_run.txt`):

- `yolo11s-oiv7.pt` — general model, ~600 classes
- `yolov5x6u.pt` — high accuracy, slower
- `yolov8n.pt` — very fast, lower accuracy (good for webcams)
- `yolov8s-pose.pt` — human pose detection
- `yolov8s-seg.pt` — segmentation models
- `yolov8x.pt` — highest accuracy, slower

Important: model weight files are large and are included locally for convenience. They are listed in `.gitignore` so they are not committed to remote repos by default.

Dependencies
------------
Minimum dependencies (see `requirements.txt`):

- Python 3.8+
- ultralytics
- opencv-python
- supervision==0.3.0
- pyqt5
- pyinstaller (for packaging)

Install using pip (recommended inside a virtualenv or conda env):

```bash
python -m pip install -r requirements.txt
```

Quick start (webcam)
--------------------
Run the provided webcam wrapper which uses the project's helpers:

```bash
python scripts/run_webcam.py --model models/yolov8n.pt --source 0
```

Replace `--source 0` with a video file path or RTSP URL for network cameras.

Run the GUI (PyQt)
------------------
Start the GUI app that wraps `app_pyqt.py`:

```bash
python scripts/run_gui.py
```

Project layout
--------------

- `app_pyqt.py` — PyQt GUI (main window `YOLOApp`).
- `webcam.py`, `webcam_yolo.py`, `yolo_inference.py` — small example scripts.
- `models/` — store `.pt` weight files here.
- `src/yolo_scan/` — package with inference helpers (`load_model`, `run_model_on_frame`, `list_model_files`).
- `scripts/` — small CLI wrappers (`run_webcam.py`, `run_gui.py`).
- `requirements.txt`, `README.md`, `LICENSE`, `.gitignore` — repo metadata.

Refactor notes and goals
------------------------
I created `src/yolo_scan` to centralize model-loading and per-frame inference. The example wrappers in `scripts/` use those helpers so logic is not duplicated between the GUI and CLI.

Known limitations & TODO
------------------------
- The ROS node examples may need topic/message adjustments for your ROS version — they were left as example stubs.
- `app_pyqt.py` contains the full GUI implementation; it was left in place and is launched via `scripts/run_gui.py`.
- Consider adding a `scripts/download_models.sh` to fetch official weights instead of committing them.

Security and secrets
--------------------
I scanned the repository for common secret tokens (`API_KEY`, `.env`, `PRIVATE_KEY`) and did not find obvious matches. If you previously pushed secrets to a remote repository, rotate those credentials and remove them from history (see guidance below).

Cleaning large files & sensitive data from git history
----------------------------------------------------
If you have large `.pt` files or secrets already present in git history, remove them with `git-filter-repo` (recommended) or BFG and then force-push:

```bash
# install git-filter-repo (pip or package manager)
pip install git-filter-repo

# example: remove all .pt files from history
git filter-repo --invert-paths --path-glob '*.pt' --path models/
git push --force
```

If secrets were committed, rotate them at the provider and remove from history before publishing.

Packaging a desktop executable (PyInstaller)
------------------------------------------
You can create a standalone executable using PyInstaller. Note: building a Windows `.exe` should be performed on Windows; building macOS `.app` should be done on macOS.

Example (create a single-folder build for the GUI):

```bash
# from repo root, with virtualenv activated
pip install pyinstaller

# Build GUI (on the platform you target)
pyinstaller --noconfirm --windowed --add-data "models:models" scripts/run_gui.py

# The output will be in `dist/run_gui/` (on macOS it may create a .app bundle)
```

Example (CLI webcam to single-file exe):

```bash
pyinstaller --onefile --add-data "models:models" scripts/run_webcam.py
# result: dist/run_webcam (single binary)
```

Notes on packaging:
- `--add-data "models:models"` instructs PyInstaller to include the `models/` folder. Adjust paths as needed.
- PyInstaller may need additional hidden-imports for `ultralytics` or `PyQt5`; if the executable fails, check the PyInstaller warnings and add `--hidden-import` flags.
- GPU/torch support: if your models require GPU, ensure the target machine has appropriate CUDA drivers and the runtime environment; packaging does not bundle drivers.

Support and next steps
----------------------
I can proceed with a full reorganization (moving `app_pyqt.py` into the `src/yolo_scan` package as `gui.py`, splitting inference logic further, and adding a `scripts/download_models.sh` and a PyInstaller spec). Tell me which of these you want me to do next:

- Move and modularize the GUI into `src/yolo_scan.gui` (yes/no)
- Add `scripts/download_models.sh` (yes/no)
- Produce Windows-targeted PyInstaller spec and a CI job example (yes/no)

