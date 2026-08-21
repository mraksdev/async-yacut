import aiohttp
from flask import flash, redirect, render_template, request

from yacut import app, db
from yacut.constants import (
    DUPLICATE_CUSTOM_ID_MESSAGE,
    RESERVED_SHORT_ID,
)
from yacut.forms import FilesUploadForm, URLMapForm
from yacut.models import URLMap
from yacut.services import yandex_disk
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
        short_link = '{}{}'.format(request.host_url, url_map.short)
    return render_template('index.html', form=form, short_link=short_link)


async def upload_files(file_storages) -> list[dict[str, str]]:
    """Upload files to Yandex Disk and shorten their download links.

    Args:
        file_storages: Werkzeug file storage objects from the form.

    Returns:
        list[dict[str, str]]: File names paired with generated short
        links.
    """
    uploaded_files: list[dict[str, str]] = []
    async with aiohttp.ClientSession() as session:
        for file_storage in file_storages:
            content = file_storage.read()
            upload_link = await yandex_disk.fetch_upload_link(
                session,
                file_storage.filename,
            )
            disk_path = await yandex_disk.upload_file(
                session,
                upload_link,
                content,
            )
            download_link = await yandex_disk.fetch_download_link(
                session,
                disk_path,
            )
            url_map = URLMap(
                original=download_link,
                short=get_unique_short_id(),
            )
            db.session.add(url_map)
            db.session.commit()
            uploaded_files.append({
                'name': file_storage.filename,
                'short_link': '{}{}'.format(request.host_url, url_map.short),
            })
    return uploaded_files


@app.route('/files', methods=['GET', 'POST'])
async def files_view() -> str:
    """Render the file upload page and handle uploads."""
    form = FilesUploadForm()
    uploaded_files: list[dict[str, str]] = []
    if form.validate_on_submit():
        uploaded_files = await upload_files(form.files.data)
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
