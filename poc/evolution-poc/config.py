import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "evolution-poc-dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EVOLUTION_BASE_URL = os.getenv("EVOLUTION_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "default")
    ENGINE_MOCK = os.getenv("ENGINE_MOCK", "false").lower() == "true"

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5002"))
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    ENGINE_LABEL = "Evolution API"
