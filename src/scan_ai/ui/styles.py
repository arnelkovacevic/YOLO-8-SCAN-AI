"""Themes, QSS stylesheets and small styling helpers."""
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

THEMES = {
    "dark": dict(bg="#0b0f19", panel="#121826", panel2="#1a2234", border="#263248",
                 text="#e6edf7", muted="#7f8ba3", video="#05070c"),
    "light": dict(bg="#eef2f8", panel="#ffffff", panel2="#f1f5fb", border="#d5dde9",
                  text="#101828", muted="#667085", video="#dfe6f1"),
}
ACCENT = "#22d3a6"
ACCENT_2 = "#3b82f6"
DANGER = "#ef4444"
WARN = "#f59e0b"


def make_qss(p):
    return f"""
    QWidget {{ background-color: {p['bg']}; color: {p['text']}; font-family: 'Helvetica Neue', 'Segoe UI', Arial; }}
    QFrame#panel, QFrame#card {{ background-color: {p['panel']}; border: 1px solid {p['border']}; border-radius: 16px; }}
    QFrame#panel QLabel, QFrame#card QLabel {{ background: transparent; }}
    QLabel#section {{ color: {p['muted']}; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-top: 8px; }}
    QLabel#title {{ color: {p['text']}; font-size: 26px; font-weight: 800; }}
    QLabel#subtitle {{ color: {p['muted']}; font-size: 12px; }}
    QLabel#muted {{ color: {p['muted']}; font-size: 13px; }}
    QLabel#name {{ font-size: 24px; font-weight: 800; color: {ACCENT}; }}
    QLabel#clock {{ color: {p['text']}; font-size: 16px; font-weight: 700; background-color: {p['panel']};
        border: 1px solid {p['border']}; border-radius: 12px; padding: 6px 16px; }}
    QLabel#chip {{ color: {p['text']}; font-size: 12px; font-weight: 600; background-color: {p['panel2']};
        border: 1px solid {p['border']}; border-radius: 10px; padding: 4px 12px; }}
    QLabel#status {{ color: {p['muted']}; font-size: 12px; padding: 4px 6px; }}
    QLabel#dets {{ color: {p['text']}; font-size: 13px; background-color: {p['panel2']};
        border: 1px solid {p['border']}; border-radius: 10px; padding: 8px 12px; }}
    QLabel#video {{ background-color: {p['video']}; border: 2px solid {p['border']}; border-radius: 16px;
        color: {p['muted']}; font-size: 16px; }}
    QLabel#tech {{ background-color: {p['panel2']}; border: 1px solid {p['border']}; border-radius: 12px;
        padding: 10px; font-size: 13px; }}
    QComboBox {{ background-color: {p['panel2']}; border: 1px solid {p['border']}; border-radius: 10px;
        padding: 8px 12px; min-height: 22px; color: {p['text']}; }}
    QComboBox:hover {{ border: 1px solid {ACCENT_2}; }}
    QComboBox::drop-down {{ border: 0; width: 26px; }}
    QComboBox QAbstractItemView {{ background-color: {p['panel2']}; border: 1px solid {p['border']};
        selection-background-color: {ACCENT_2}; selection-color: white; color: {p['text']}; outline: 0; }}
    QSlider::groove:horizontal {{ height: 6px; background: {p['panel2']}; border: 1px solid {p['border']}; border-radius: 3px; }}
    QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 3px; }}
    QSlider::handle:horizontal {{ background: white; border: 1px solid {p['border']}; width: 16px; margin: -6px 0; border-radius: 8px; }}
    QPushButton#lang, QPushButton#tool {{ background-color: {p['panel2']}; border: 1px solid {p['border']};
        border-radius: 10px; padding: 6px 12px; font-size: 14px; font-weight: 700; color: {p['muted']}; }}
    QPushButton#lang:hover, QPushButton#tool:hover {{ border: 1px solid {ACCENT_2}; color: {p['text']}; }}
    QPushButton#lang:checked {{ background-color: {ACCENT_2}; border: 1px solid {ACCENT_2}; color: white; }}
    """


def btn_qss(color, hover):
    return f"""
        QPushButton {{ background-color: {color}; color: white; border: none; border-radius: 12px;
            padding: 12px; font-size: 14px; font-weight: 700; }}
        QPushButton:hover {{ background-color: {hover}; }}
        QPushButton:pressed {{ padding-top: 14px; }}
    """


def ghost_qss(p):
    return f"""
        QPushButton {{ background-color: transparent; color: {p['muted']}; border: 1px solid {p['border']};
            border-radius: 12px; padding: 10px; font-size: 13px; font-weight: 600; }}
        QPushButton:hover {{ color: {p['text']}; border: 1px solid {DANGER}; }}
    """



def shadow(widget, blur=30, alpha=90):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(blur)
    fx.setOffset(0, 6)
    fx.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(fx)
