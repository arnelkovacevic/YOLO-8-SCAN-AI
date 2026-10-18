from PyQt5.QtCore import QThread, pyqtSignal


# -------------------------
# Worker thread (capture + YOLO inference off the UI thread)
# -------------------------
class DetectWorker(QThread):
    frame_ready = pyqtSignal(object, list)   # annotated BGR frame, class names
    failed = pyqtSignal()

    def __init__(self, cap, model, conf):
        super().__init__()
        self.cap, self.model, self.conf = cap, model, conf
        self._stop = False
        self.ui_ready = True   # back-pressure: skip frames while UI is still painting

    def stop(self):
        self._stop = True
        self.wait(3000)

    def run(self):
        while not self._stop:
            ret, frame = self.cap.read()
            if not ret:
                self.failed.emit()
                return
            res = self.model(frame, conf=self.conf, verbose=False)[0]
            if not self.ui_ready:
                continue
            names = [res.names[int(c)] for c in res.boxes.cls] if res.boxes is not None else []
            self.ui_ready = False
            self.frame_ready.emit(res.plot(), names)
