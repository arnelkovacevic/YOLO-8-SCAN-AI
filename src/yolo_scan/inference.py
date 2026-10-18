"""Simple inference helpers to centralize model loading and per-frame inference.

This module keeps a small stable API so scripts and the GUI can reuse
the same logic without duplicating code.
"""
from typing import List
import os
import cv2
from ultralytics import YOLO


def list_model_files(models_dir: str = "models") -> List[str]:
    """Return list of model filenames (basename) in `models_dir` ending with .pt.

    If the directory does not exist, returns an empty list.
    """
    if not os.path.isdir(models_dir):
        return []
    files = [f for f in os.listdir(models_dir) if f.endswith(".pt")]
    return files


def load_model(model_path: str):
    """Load and return a YOLO model instance.

    `model_path` can be an absolute path or relative to project root.
    """
    return YOLO(model_path)


def run_model_on_frame(model, frame):
    """Run model on a single BGR frame and return an annotated BGR image.

    The function uses the Ultralytics YOLO API which returns results; we
    call `.plot()` on the first result to get an annotated image.
    """
    results = model(frame, verbose=False)
    annotated = results[0].plot()
    return annotated


def open_camera(source=0):
    """Open and return a cv2.VideoCapture for given source.

    `source` can be an int index or a string for file/RTSP.
    """
    cap = cv2.VideoCapture(source)
    return cap
