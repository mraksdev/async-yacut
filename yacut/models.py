from datetime import datetime

from yacut import db


class URLMap(db.Model):
    """Database model that maps an original URL to a short identifier."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __str__(self) -> str:
        return self.short

    def __repr__(self) -> str:
        return '<URLMap {} -> {}>'.format(self.original, self.short)
