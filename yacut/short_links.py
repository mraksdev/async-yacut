import re
from random import choice

from yacut import db
from yacut.constants import (
    ALLOWED_CHARACTERS,
    CUSTOM_ID_PATTERN,
    MAX_CUSTOM_ID_LENGTH,
    RESERVED_SHORT_ID,
    SHORT_ID_LENGTH,
)
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


def is_valid_custom_id(custom_id: str) -> bool:
    """Check a user-provided identifier against format rules.

    Args:
        custom_id: Candidate short identifier.

    Returns:
        bool: True when the identifier fits the length limit and
        contains only allowed characters.
    """
    return (
        len(custom_id) <= MAX_CUSTOM_ID_LENGTH
        and re.fullmatch(CUSTOM_ID_PATTERN, custom_id) is not None
    )


def is_short_id_taken(short_id: str) -> bool:
    """Check whether an identifier is reserved or already stored.

    Args:
        short_id: Candidate short identifier.

    Returns:
        bool: True when the identifier cannot be used for a new link.
    """
    return short_id == RESERVED_SHORT_ID or (
        URLMap.query.filter_by(short=short_id).first() is not None
    )


def create_url_map(original: str, short: str = '') -> URLMap:
    """Persist a new URL mapping.

    Args:
        original: Original long URL.
        short: Custom short identifier; generated when omitted.

    Returns:
        URLMap: The created database object.
    """
    url_map = URLMap(
        original=original,
        short=short or get_unique_short_id(),
    )
    db.session.add(url_map)
    db.session.commit()
    return url_map
