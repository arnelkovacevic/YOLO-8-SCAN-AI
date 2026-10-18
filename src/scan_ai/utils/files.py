"""File helpers: model and sample-image discovery."""
from .paths import MODELS_DIR, SAMPLES_DIR

IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def load_models():
    MODELS_DIR.mkdir(exist_ok=True)
    return sorted(p.name for p in MODELS_DIR.iterdir() if p.suffix == ".pt")


def load_sample_images():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(p.name for p in SAMPLES_DIR.iterdir() if p.suffix.lower() in IMG_EXT)
