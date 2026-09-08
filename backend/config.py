
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ---------------------------------------------------------
    # Flask
    # ---------------------------------------------------------

    SECRET_KEY = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-secret-change-in-production"
    )


    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    db_url = os.getenv("DATABASE_URL", "sqlite:///resume_builder.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax" if os.getenv("FLASK_DEBUG", "True").lower() == "true" else "None")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False" if os.getenv("FLASK_DEBUG", "True").lower() == "true" else "True").lower() == "true"


    # ---------------------------------------------------------
    # Email / SMTP
    # ---------------------------------------------------------

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.getenv("MAIL_PORT", "587")
    )

    MAIL_USE_TLS = (
        os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    )

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")


    # ---------------------------------------------------------
    # AI API Keys
    # ---------------------------------------------------------

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")


    # ---------------------------------------------------------
    # Admin
    # ---------------------------------------------------------

    ADMIN_EMAIL = os.getenv(
        "ADMIN_EMAIL",
        "admin@example.com"
    )


    # ---------------------------------------------------------
    # File Uploads
    # ---------------------------------------------------------

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "uploads"
    )

    OUTPUT_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "outputs"
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    ALLOWED_EXTENSIONS = {
        "pdf",
        "docx"
    }