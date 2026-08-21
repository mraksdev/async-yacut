"""Project-wide constants."""

import string

MAX_CUSTOM_ID_LENGTH: int = 16
SHORT_ID_LENGTH: int = 6

CUSTOM_ID_PATTERN: str = r'^[A-Za-z0-9]+$'

ALLOWED_CHARACTERS: tuple[str, ...] = tuple(
    string.ascii_letters + string.digits,
)

INVALID_CUSTOM_ID_MESSAGE: str = (
    'Указано недопустимое имя для короткой ссылки'
)

DUPLICATE_CUSTOM_ID_MESSAGE: str = (
    'Предложенный вариант короткой ссылки уже существует.'
)

RESERVED_SHORT_ID: str = 'files'

NOT_FOUND_MESSAGE: str = 'Указанный id не найден'
