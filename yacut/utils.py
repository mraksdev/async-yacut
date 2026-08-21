from random import choice

from yacut.constants import ALLOWED_CHARACTERS, SHORT_ID_LENGTH
from yacut.models import URLMap


def get_unique_short_id() -> str:
    """Generate a short identifier absent from the database.

    Returns:
        str: Random identifier of ``SHORT_ID_LENGTH`` characters built
        from ``ALLOWED_CHARACTERS``.
    """
    while True:
        short_id = ''.join(
            choice(ALLOWED_CHARACTERS)
            for _ in range(SHORT_ID_LENGTH)
        )
        if URLMap.query.filter_by(short=short_id).first() is None:
            return short_id
