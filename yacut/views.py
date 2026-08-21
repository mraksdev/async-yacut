import asyncio

import aiohttp
from flask import Response, flash, redirect, render_template, request

from yacut import app
from yacut.constants import (
    DUPLICATE_CUSTOM_ID_MESSAGE,
    UPLOAD_ERROR_MESSAGE,
)
from yacut.forms import FilesUploadForm, URLMapForm
from yacut.models import URLMap
from yacut.services import yandex_disk
from yacut.utils import create_url_map, is_short_id_taken


@app.route('/', methods=['GET', 'POST'])
def index_view() -> str:
    """Render the index page and create short links."""
    form = URLMapForm()
    short_link = None
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        if custom_id and is_short_id_taken(custom_id):
            flash(DUPLICATE_CUSTOM_ID_MESSAGE)
            return render_template('index.html', form=form)
        url_map = create_url_map(form.original_link.data, custom_id)
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
    failed_uploads: int = 0
    async with aiohttp.ClientSession() as session:
        for file_storage in file_storages:
            try:
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
            except (
                aiohttp.ClientError,
                asyncio.TimeoutError,
                KeyError,
            ):
                failed_uploads += 1
                continue
            url_map = create_url_map(download_link)
            uploaded_files.append({
                'name': file_storage.filename,
                'short_link': '{}{}'.format(request.host_url, url_map.short),
            })
    if failed_uploads:
        flash(UPLOAD_ERROR_MESSAGE)
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
def redirect_view(short_id: str) -> Response:
    """Redirect a short link to its original URL."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
