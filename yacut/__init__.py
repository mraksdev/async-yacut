"""YaCut application package — a link shortening service."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from yacut.settings import Config

app: Flask = Flask(__name__)
app.config.from_object(Config)
db: SQLAlchemy = SQLAlchemy(app)

from yacut import models  # noqa: E402, F401
