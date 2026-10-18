from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout

from .styles import ACCENT_2, btn_qss, shadow

AUTHOR = "Arnel Kovacevic"
TECH = [
    ("🐍", "Python 3.10", "Core language"),
    ("🖼️", "PyQt5", "GUI · QThread · QSS"),
    ("🎯", "Ultralytics YOLO", "YOLOv8 / YOLO11"),
    ("👁️", "OpenCV", "Video capture & drawing"),
    ("🔥", "PyTorch", "Deep-learning backend"),
    ("🔢", "NumPy", "Array processing"),
]


class InfoDialog(QDialog):
    def __init__(self, parent, t):
        super().__init__(parent)
        self.setWindowTitle(t("info_title"))
        self.setModal(True)
        self.setMinimumWidth(620)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 24, 26, 22)
        lay.setSpacing(10)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 18, 22, 18)
        cl.setSpacing(4)
        small = QLabel(t("info_author").upper())
        small.setObjectName("section")
        name = QLabel(AUTHOR)
        name.setObjectName("name")
        cl.addWidget(small)
        cl.addWidget(name)
        lay.addWidget(card)
        shadow(card)

        for key, obj in (("info_desc", "muted"), ("info_features", "muted")):
            lbl = QLabel(t(key))
            lbl.setObjectName(obj)
            lbl.setWordWrap(True)
            lay.addWidget(lbl)

        head = QLabel(t("info_tech"))
        head.setObjectName("section")
        lay.addWidget(head)

        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (icon, title, sub) in enumerate(TECH):
            lbl = QLabel(f"<span style='font-size:20px'>{icon}</span><br>"
                         f"<b>{title}</b><br><span style='color:{parent.p['muted']};font-size:11px'>{sub}</span>")
            lbl.setObjectName("tech")
            lbl.setTextFormat(Qt.RichText)
            lbl.setMinimumHeight(92)
            grid.addWidget(lbl, i // 3, i % 3)
        lay.addLayout(grid)

        close = QPushButton(t("close"))
        close.setCursor(Qt.PointingHandCursor)
        close.setStyleSheet(btn_qss(ACCENT_2, "#2563eb"))
        close.clicked.connect(self.accept)
        lay.addSpacing(6)
        lay.addWidget(close)
