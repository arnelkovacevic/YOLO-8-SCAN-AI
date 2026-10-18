"""Small wrapper script to run webcam inference using `src/yolo_scan` helpers.

Usage:
    python scripts/run_webcam.py --model models/yolov8n.pt --source 0
"""
import argparse
import cv2
import os
import sys

# Ensure project src is on sys.path when running from repo root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.yolo_scan import load_model, run_model_on_frame


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="models/yolov8n.pt", help="Path to .pt model")
    p.add_argument("--source", default=0, help="Video source (index or path)")
    args = p.parse_args()

    model_path = args.model
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        print("Place your .pt file in the models/ directory or pass --model path")
        return

    model = load_model(model_path)

    # source may be int
    try:
        src = int(args.source)
    except ValueError:
        src = args.source

    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        print(f"Unable to open source: {args.source}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        annotated = run_model_on_frame(model, frame)
        cv2.imshow("YOLO Webcam", annotated)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
