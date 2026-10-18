import os
import time
import datetime
from collections import Counter

import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QSlider, QFrame,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QButtonGroup, QFileDialog
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO

from ..core.camera import get_available_cameras
from ..core.detector import DetectWorker
from ..i18n import TR
from ..utils.files import load_models, load_sample_images
from ..utils.paths import MODELS_DIR, OUTPUT_DIR, SAMPLES_DIR
from .info_dialog import InfoDialog
from .styles import (
    ACCENT, ACCENT_2, DANGER, WARN, THEMES, make_qss, btn_qss, ghost_qss, shadow
)


class YOLOApp(QWidget):
    OTHER = "__other__"

    def __init__(self):
        super().__init__()
        self.lang = "it"
        self.theme = "dark"
        self.p = THEMES[self.theme]
        self.models = load_models()
        self.cameras = get_available_cameras()
        self.model = None
        self.model_name = None
        self.cap = None
        self.worker = None
        self.recording = False
        self.video_writer = None
        self.last_frame = None
        self.running = False
        self.image_mode = False
        self._fps = 0.0
        self._last_t = time.time()
        self._count = 0
        self._status_key = ("ready", ())
        self._dets = Counter()

        self.resize(1480, 900)
        self.setMinimumSize(1100, 720)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 18, 24, 12)
        root.setSpacing(14)

        # ---- Header
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(0)
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subtitle")
        titles.addWidget(self.title_label)
        titles.addWidget(self.subtitle_label)
        header.addLayout(titles)
        header.addStretch(1)

        self.info_btn = QPushButton()
        self.info_btn.setObjectName("tool")
        self.info_btn.setCursor(Qt.PointingHandCursor)
        self.info_btn.clicked.connect(self.show_info)
        header.addWidget(self.info_btn)

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("tool")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_btn)
        header.addSpacing(8)

        self.it_btn = QPushButton("🇮🇹  IT")
        self.en_btn = QPushButton("🇬🇧  EN")
        group = QButtonGroup(self)
        group.setExclusive(True)
        for b, code in ((self.it_btn, "it"), (self.en_btn, "en")):
            b.setObjectName("lang")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            group.addButton(b)
            b.clicked.connect(lambda _=False, c=code: self.set_language(c))
            header.addWidget(b)
        self.it_btn.setChecked(True)
        header.addSpacing(14)

        self.clock_label = QLabel()
        self.clock_label.setObjectName("clock")
        self.clock_label.setAlignment(Qt.AlignCenter)
        header.addWidget(self.clock_label)
        root.addLayout(header)

        # ---- Content
        content = QHBoxLayout()
        content.setSpacing(18)

        video_col = QVBoxLayout()
        self.video = QLabel()
        self.video.setObjectName("video")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setMinimumSize(640, 400)
        self.video.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        shadow(self.video)
        video_col.addWidget(self.video, 1)

        chips = QHBoxLayout()
        self.live_chip = QLabel()
        self.fps_chip = QLabel("FPS 0")
        self.obj_chip = QLabel()
        for c in (self.live_chip, self.fps_chip, self.obj_chip):
            c.setObjectName("chip")
            chips.addWidget(c)
        chips.addStretch(1)
        video_col.addLayout(chips)
        content.addLayout(video_col, 4)

        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(340)
        shadow(panel)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(20, 14, 20, 20)
        pl.setSpacing(6)

        self.source_lbl = QLabel()
        self.source_lbl.setObjectName("section")
        pl.addWidget(self.source_lbl)
        self.source_dd = QComboBox()
        self.source_dd.currentIndexChanged.connect(self._on_source_change)
        pl.addWidget(self.source_dd)

        self.url_input = QComboBox()
        self.url_input.setEditable(True)
        self.url_input.setVisible(False)
        pl.addWidget(self.url_input)

        self.model_lbl = QLabel()
        self.model_lbl.setObjectName("section")
        pl.addWidget(self.model_lbl)
        self.model_dd = QComboBox()
        pl.addWidget(self.model_dd)

        self.conf_lbl = QLabel()
        self.conf_lbl.setObjectName("section")
        pl.addWidget(self.conf_lbl)
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(5, 95)
        self.conf_slider.setValue(25)
        self.conf_slider.valueChanged.connect(self._on_conf_change)
        pl.addWidget(self.conf_slider)

        self.image_lbl = QLabel()
        self.image_lbl.setObjectName("section")
        pl.addWidget(self.image_lbl)
        self.image_dd = QComboBox()
        pl.addWidget(self.image_dd)
        img_row = QHBoxLayout()
        self.browse_btn, self.analyze_btn = QPushButton(), QPushButton()
        for b in (self.browse_btn, self.analyze_btn):
            b.setObjectName("tool")
            b.setCursor(Qt.PointingHandCursor)
            img_row.addWidget(b)
        self.browse_btn.clicked.connect(self.browse_image)
        self.analyze_btn.clicked.connect(self.analyze_image)
        pl.addLayout(img_row)

        self.det_lbl = QLabel()
        self.det_lbl.setObjectName("section")
        pl.addWidget(self.det_lbl)
        self.det_box = QLabel()
        self.det_box.setObjectName("dets")
        self.det_box.setWordWrap(True)
        self.det_box.setMinimumHeight(70)
        self.det_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        pl.addWidget(self.det_box)

        pl.addSpacing(10)
        self.start_btn, self.stop_btn = QPushButton(), QPushButton()
        self.shot_btn, self.record_btn, self.exit_btn = QPushButton(), QPushButton(), QPushButton()
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.shot_btn.clicked.connect(self.take_screenshot)
        self.record_btn.clicked.connect(lambda: self.toggle_record())
        self.exit_btn.clicked.connect(self.close)
        btn_col = QVBoxLayout()
        btn_col.setSpacing(12)
        for b in (self.start_btn, self.stop_btn, self.shot_btn, self.record_btn):
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(46)
            btn_col.addWidget(b)
        pl.addLayout(btn_col)
        pl.addStretch(1)
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        pl.addWidget(self.exit_btn)
        content.addWidget(panel, 0)
        root.addLayout(content, 1)

        self.status = QLabel()
        self.status.setObjectName("status")
        root.addWidget(self.status)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.apply_theme()
        self.retranslate()

    # -------------------------
    # Theme
    # -------------------------
    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.p = THEMES[self.theme]
        self.apply_theme()

    def apply_theme(self):
        p = self.p
        self.setStyleSheet(make_qss(p))
        self.title_label.setText(f"<span style='color:{ACCENT}'>●</span> SCAN AI "
                                 f"<span style='color:{p['muted']};font-weight:400'>| Orizon-AIX</span>")
        self.theme_btn.setText("🌙" if self.theme == "dark" else "☀️")
        self.start_btn.setStyleSheet(btn_qss(ACCENT, "#1fbd95"))
        self.stop_btn.setStyleSheet(btn_qss(DANGER, "#dc2626"))
        self.shot_btn.setStyleSheet(btn_qss(WARN, "#d97706"))
        self._style_record_btn()
        self.exit_btn.setStyleSheet(ghost_qss(p))
        self.live_chip.setStyleSheet(f"color: {ACCENT};" if self.running else "")

    def _style_record_btn(self):
        self.record_btn.setStyleSheet(
            btn_qss("#b91c1c", "#dc2626") if self.recording else btn_qss(ACCENT_2, "#2563eb"))

    # -------------------------
    # i18n
    # -------------------------
    def t(self, key):
        return TR[self.lang][key]

    def set_language(self, code):
        if code != self.lang:
            self.lang = code
            self.retranslate()

    def retranslate(self):
        src_data = self.source_dd.currentData()
        model_idx = self.model_dd.currentIndex()

        self.subtitle_label.setText(self.t("subtitle"))
        self.source_lbl.setText(self.t("source"))
        self.model_lbl.setText(self.t("model"))
        self.det_lbl.setText(self.t("detections"))
        self.image_lbl.setText(self.t("image"))
        self.browse_btn.setText(self.t("browse"))
        self.analyze_btn.setText(self.t("analyze"))
        self.refresh_images()
        self.url_input.lineEdit().setPlaceholderText(self.t("url_ph"))
        self.start_btn.setText(self.t("start"))
        self.stop_btn.setText(self.t("stop"))
        self.shot_btn.setText(self.t("shot"))
        self.record_btn.setText(self.t("rec_stop") if self.recording else self.t("rec"))
        self.exit_btn.setText(self.t("exit"))
        self.info_btn.setText(self.t("info_btn"))
        self.theme_btn.setToolTip(self.t("theme_tip"))
        self.live_chip.setText(f"● {self.t('live')}" if self.running else "○ OFF")
        self.obj_chip.setText(f"{self.t('objects')}: {self._count}")
        self._on_conf_change()
        self._render_dets()

        self.source_dd.blockSignals(True)
        self.source_dd.clear()
        for i in self.cameras:
            self.source_dd.addItem(f"📷  {self.t('webcam')} {i}", i)
        self.source_dd.addItem(f"🌐  {self.t('other_source')}", self.OTHER)
        idx = self.source_dd.findData(src_data) if src_data is not None else 0
        self.source_dd.setCurrentIndex(max(idx, 0))
        self.source_dd.blockSignals(False)
        self._on_source_change()

        self.model_dd.clear()
        self.model_dd.addItem(self.t("choose_model"))
        self.model_dd.addItems(self.models)
        self.model_dd.setCurrentIndex(max(model_idx, 0))

        if not self.running and not self.image_mode:
            self.video.setText(self.t("idle") if self.last_frame is None else self.t("off"))
        self.set_status(self._status_key[0], *self._status_key[1])
        self.update_clock()

    def set_status(self, key, *args):
        self._status_key = (key, args)
        self.status.setText(self.t(key).format(*args))

    def _on_conf_change(self):
        v = self.conf_slider.value() / 100
        self.conf_lbl.setText(f"{self.t('conf')}  ·  {v:.2f}")
        if self.worker:
            self.worker.conf = v

    def _render_dets(self):
        if not self._dets:
            self.det_box.setText(f"<span style='color:{self.p['muted']}'>{self.t('nothing')}</span>")
            return
        rows = [f"<b>{n}</b> <span style='color:{ACCENT}'>×{c}</span>"
                for n, c in self._dets.most_common(6)]
        self.det_box.setText("<br>".join(rows))

    def refresh_images(self, select=None):
        current = select or self.image_dd.currentData()
        self.image_dd.clear()
        files = load_sample_images()
        if not files and not current:
            self.image_dd.addItem(self.t("no_images"), None)
        for f in files:
            self.image_dd.addItem(f"🖼  {f}", str(SAMPLES_DIR / f))
        if current and self.image_dd.findData(current) < 0:
            self.image_dd.addItem(f"🖼  {os.path.basename(current)}", current)
        idx = self.image_dd.findData(current) if current else 0
        self.image_dd.setCurrentIndex(max(idx, 0))

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.t("pick_img"), str(SAMPLES_DIR),
            "Images (*.jpg *.jpeg *.png *.bmp *.webp)")
        if path:
            self.refresh_images(select=path)
            self.analyze_image()

    def analyze_image(self):
        path = self.image_dd.currentData()
        if not path:
            self.set_status("no_images")
            return
        if self.model_dd.currentIndex() <= 0:
            self.set_status("err_model")
            return
        name = self.model_dd.currentText()
        img = cv2.imread(path)
        if img is None:
            self.set_status("err_img", path)
            return
        if self.model is None or self.model_name != name:
            self.set_status("loading", name)
            QApplication.processEvents()
            try:
                self.model = YOLO(str(MODELS_DIR / name))
                self.model_name = name
            except Exception as e:
                self.model = None
                self.set_status("err_load", e)
                return
        self.stop_camera()
        res = self.model(img, conf=self.conf_slider.value() / 100, verbose=False)[0]
        names = [res.names[int(c)] for c in res.boxes.cls] if res.boxes is not None else []
        annotated = res.plot()
        self.last_frame = annotated
        self.image_mode = True
        self._count = len(names)
        self._dets = Counter(names)
        self._render_dets()
        self.obj_chip.setText(f"{self.t('objects')}: {self._count}")
        self._show_frame(annotated)
        self.set_status("img_done", os.path.basename(path), name, self._count)

    def _show_frame(self, bgr):
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video.setPixmap(QPixmap.fromImage(img).scaled(
            self.video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def show_info(self):
        InfoDialog(self, self.t).exec_()

    # -------------------------
    # Logic
    # -------------------------
    def _on_source_change(self):
        self.url_input.setVisible(self.source_dd.currentData() == self.OTHER)

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.setText(f"{now.strftime(self.t('date_fmt'))}   {now.strftime('%H:%M:%S')}")

    def _stop_worker(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        if self.cap:
            self.cap.release()
            self.cap = None

    def start_camera(self):
        if self.model_dd.currentIndex() <= 0:
            self.set_status("err_model")
            return
        name = self.model_dd.currentText()

        data = self.source_dd.currentData()
        if data == self.OTHER:
            source = self.url_input.currentText().strip()
            if not source:
                self.set_status("err_url")
                return
        else:
            source = data

        if self.model is None or self.model_name != name:
            self.set_status("loading", name)
            QApplication.processEvents()
            try:
                self.model = YOLO(str(MODELS_DIR / name))
                self.model_name = name
            except Exception as e:
                self.model = None
                self.set_status("err_load", e)
                return

        self._stop_worker()
        self.image_mode = False
        self.cap = cv2.VideoCapture(source)
        if isinstance(source, str):
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.cap.isOpened():
            self.cap = None
            self.set_status("err_open", source)
            return

        self.worker = DetectWorker(self.cap, self.model, self.conf_slider.value() / 100)
        self.worker.frame_ready.connect(self.on_frame)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

        self.running = True
        self._last_t, self._fps = time.time(), 0.0
        self.live_chip.setText(f"● {self.t('live')}")
        self.live_chip.setStyleSheet(f"color: {ACCENT};")
        self.set_status("started", name, source)

    def on_failed(self):
        self.running = False
        self.live_chip.setText("○ OFF")
        self.live_chip.setStyleSheet("")
        self.set_status("err_lost")

    def stop_camera(self):
        self.running = False
        self.image_mode = False
        self._stop_worker()
        if self.recording:
            self.toggle_record(silent=True)
        self.last_frame = None
        self._count = 0
        self._dets = Counter()
        self._render_dets()
        self.video.clear()
        self.video.setText(self.t("off"))
        self.live_chip.setText("○ OFF")
        self.live_chip.setStyleSheet("")
        self.fps_chip.setText("FPS 0")
        self.obj_chip.setText(f"{self.t('objects')}: 0")
        self.set_status("stopped")

    def take_screenshot(self):
        if self.last_frame is None or not (self.running or self.image_mode):
            self.set_status("no_cam")
            return
        OUTPUT_DIR.mkdir(exist_ok=True)
        name = str(OUTPUT_DIR / f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(name, self.last_frame)
        self.set_status("saved", name)

    def toggle_record(self, silent=False):
        if self.recording:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            self.record_btn.setText(self.t("rec"))
            self._style_record_btn()
            if not silent:
                self.set_status("rec_done")
            return
        if self.last_frame is None or not self.running:
            self.set_status("no_cam")
            return
        OUTPUT_DIR.mkdir(exist_ok=True)
        name = str(OUTPUT_DIR / f"record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
        h, w, _ = self.last_frame.shape
        self.video_writer = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"XVID"), 20.0, (w, h))
        self.recording = True
        self.record_btn.setText(self.t("rec_stop"))
        self._style_record_btn()
        self.set_status("recording", name)

    def on_frame(self, annotated, names):
        self.last_frame = annotated
        if self.recording and self.video_writer:
            self.video_writer.write(annotated)

        now = time.time()
        dt = now - self._last_t
        self._last_t = now
        if dt > 0:
            inst = 1.0 / dt
            self._fps = 0.9 * self._fps + 0.1 * inst if self._fps else inst
        self.fps_chip.setText(f"FPS {self._fps:.0f}")
        self._count = len(names)
        self.obj_chip.setText(f"{self.t('objects')}: {self._count}")
        self._dets = Counter(names)
        self._render_dets()

        self._show_frame(annotated)
        if self.worker:
            self.worker.ui_ready = True

    def closeEvent(self, e):
        self.running = False
        if self.recording:
            self.toggle_record(silent=True)
        self._stop_worker()
        e.accept()
