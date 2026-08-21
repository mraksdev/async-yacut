import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask application configuration settings."""

    SECRET_KEY: str = os.getenv('SECRET_KEY', 'yacut-secret-key')
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        'DATABASE_URI',
        'sqlite:///db.sqlite3',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
