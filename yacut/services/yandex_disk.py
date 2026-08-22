"""Async client for the Yandex Disk REST API."""

import os
from urllib.parse import unquote

import aiohttp

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

UPLOAD_LINK_URL = '{}{}{}'.format(
    API_HOST,
    API_VERSION,
    '/disk/resources/upload',
)
DOWNLOAD_LINK_URL = '{}{}{}'.format(
    API_HOST,
    API_VERSION,
    '/disk/resources/download',
)


def get_auth_headers() -> dict[str, str]:
    """Build authorization headers for the Yandex Disk API.

    Returns:
        dict[str, str]: Headers with the OAuth token taken from the
        ``DISK_TOKEN`` environment variable.
    """
    return {
        'Authorization': 'OAuth {}'.format(os.getenv('DISK_TOKEN')),
    }


async def fetch_upload_link(
    session: aiohttp.ClientSession,
    file_name: str,
) -> str:
    """Request an upload URL for a file from the Yandex Disk API.

    Args:
        session: HTTP client session.
        file_name: Name of the file to upload.

    Returns:
        str: Prepared upload URL.
    """
    params = {
        'path': 'app:/' + file_name,
        'overwrite': 'true',
    }
    async with session.get(
        UPLOAD_LINK_URL,
        params=params,
        headers=get_auth_headers(),
    ) as response:
        data = await response.json()
        return data['href']


async def upload_file(
    session: aiohttp.ClientSession,
    upload_link: str,
    content: bytes,
) -> str:
    """Upload file contents to the given upload URL.

    Args:
        session: HTTP client session.
        upload_link: Upload URL obtained from ``fetch_upload_link``.
        content: Raw file bytes.

    Returns:
        str: Path of the uploaded file on Yandex Disk.
    """
    async with session.put(upload_link, data=content) as response:
        location = response.headers['Location']
        return unquote(location).replace('/disk', '', 1)


async def fetch_download_link(
    session: aiohttp.ClientSession,
    disk_path: str,
) -> str:
    """Request a public download URL for a file on Yandex Disk.

    Args:
        session: HTTP client session.
        disk_path: Path of the file on Yandex Disk.

    Returns:
        str: Direct download URL.
    """
    params = {'path': disk_path}
    async with session.get(
        DOWNLOAD_LINK_URL,
        params=params,
        headers=get_auth_headers(),
    ) as response:
        data = await response.json()
        return data['href']


async def upload_file_to_disk(
    session: aiohttp.ClientSession,
    file_name: str,
    content: bytes,
) -> str:
    """Run the full upload flow for a single file.

    Args:
        session: HTTP client session.
        file_name: Name of the file to upload.
        content: Raw file bytes.

    Returns:
        str: Direct download URL of the uploaded file.
    """
    upload_link = await fetch_upload_link(session, file_name)
    disk_path = await upload_file(session, upload_link, content)
    return await fetch_download_link(session, disk_path)
