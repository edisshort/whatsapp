import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "waha-poc-dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_HTTPONLY = True

    WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://127.0.0.1:3000").rstrip("/")
    WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
    WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
    ENGINE_MOCK = os.getenv("ENGINE_MOCK", "false").lower() == "true"

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5001"))
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    ENGINE_LABEL = "WAHA"
