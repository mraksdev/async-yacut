from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from yacut.constants import (
    CUSTOM_ID_PATTERN,
    INVALID_CUSTOM_ID_MESSAGE,
    MAX_CUSTOM_ID_LENGTH,
)


class URLMapForm(FlaskForm):
    """Form for creating a short link on the index page."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Укажите ссылку')],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(
                max=MAX_CUSTOM_ID_LENGTH,
                message=INVALID_CUSTOM_ID_MESSAGE,
            ),
            Regexp(CUSTOM_ID_PATTERN, message=INVALID_CUSTOM_ID_MESSAGE),
        ],
    )


class FilesUploadForm(FlaskForm):
    """Form for uploading multiple files to Yandex Disk."""

    files = MultipleFileField(
        'Файлы для загрузки',
        validators=[DataRequired(message='Выберите файлы')],
    )
