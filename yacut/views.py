from flask import flash, redirect, render_template, request

from yacut import app, db
from yacut.constants import (
    DUPLICATE_CUSTOM_ID_MESSAGE,
    RESERVED_SHORT_ID,
)
from yacut.forms import FilesUploadForm, URLMapForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view() -> str:
    """Render the index page and create short links."""
    form = URLMapForm()
    short_link = None
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        is_taken = custom_id == RESERVED_SHORT_ID or (
            URLMap.query.filter_by(short=custom_id).first() is not None
        )
        if custom_id and is_taken:
            flash(DUPLICATE_CUSTOM_ID_MESSAGE)
            return render_template('index.html', form=form)
        url_map = URLMap(
            original=form.original_link.data,
            short=custom_id or get_unique_short_id(),
        )
        db.session.add(url_map)
        db.session.commit()
        short_link = f'{request.host_url}{url_map.short}'
    return render_template('index.html', form=form, short_link=short_link)


@app.route('/files', methods=['GET', 'POST'])
async def files_view() -> str:
    """Render the file upload page."""
    form = FilesUploadForm()
    uploaded_files: list[dict[str, str]] = []
    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files,
    )


@app.route('/<string:short_id>')
def redirect_view(short_id: str) -> str:
    """Redirect a short link to its original URL."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
