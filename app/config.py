import os


class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

    TITLE = os.environ.get("TITLE", "mY-caly-crawler")
    HOST_URL = os.environ.get("HOST_URL", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 8080))

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")