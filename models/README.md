# Models

Put YOLO `.pt` weights in this folder – the app lists every `.pt` file here automatically.

| File | Type | Notes |
|---|---|---|
| `yolov8n.pt` | Detection | Very fast, lowest accuracy – good for webcams |
| `yolov8x.pt` | Detection | Highest accuracy, slow (>100 MB, not in Git – use `scripts/download_models.py`) |
| `yolov5x6u.pt` | Detection | High accuracy, detailed objects, slow (>100 MB, not in Git) |
| `yolov8s-seg.pt` | Segmentation | Precise object shapes |
| `yolov8s-pose.pt` | Pose | Human body keypoints |
| `yolo11s-oiv7.pt` | Detection | Open Images V7, 600+ classes |
| `best.pt` | Custom | Custom-trained model (TODO: document classes/dataset) |
| `helmet.pt` | Custom | Custom-trained helmet model (TODO: document classes/dataset) |
