from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024 #100 mb limit