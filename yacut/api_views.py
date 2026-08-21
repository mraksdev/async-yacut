"""API endpoints for the YaCut service."""

from flask import Response, jsonify, request

from yacut import app
from yacut.constants import (
    DUPLICATE_CUSTOM_ID_MESSAGE,
    INVALID_CUSTOM_ID_MESSAGE,
    NOT_FOUND_MESSAGE,
)
from yacut.models import URLMap
from yacut.utils import create_url_map, is_short_id_taken, is_valid_custom_id

EMPTY_BODY_MESSAGE: str = 'Отсутствует тело запроса'
REQUIRED_URL_MESSAGE: str = '"url" является обязательным полем!'


@app.route('/api/id/', methods=['POST'])
def create_short_link() -> tuple[Response, int]:
    """Create a new short link from a JSON payload.

    Returns:
        tuple[Response, int]: JSON response with the created link and
        the 201 status code, or an error message with 400.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': EMPTY_BODY_MESSAGE}), 400
    url = data.get('url')
    if not url:
        return jsonify({'message': REQUIRED_URL_MESSAGE}), 400
    custom_id = data.get('custom_id')
    if custom_id:
        if not is_valid_custom_id(custom_id):
            return jsonify({'message': INVALID_CUSTOM_ID_MESSAGE}), 400
        if is_short_id_taken(custom_id):
            return jsonify({'message': DUPLICATE_CUSTOM_ID_MESSAGE}), 400
    url_map = create_url_map(url, custom_id)
    return jsonify({
        'url': url_map.original,
        'short_link': '{}{}'.format(request.host_url, url_map.short),
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id: str) -> tuple[Response, int]:
    """Return the original URL stored for the given identifier.

    Args:
        short_id: Short identifier from the request path.

    Returns:
        tuple[Response, int]: JSON response with the original URL and
        the 200 status code, or an error message with 404.
    """
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        return jsonify({'message': NOT_FOUND_MESSAGE}), 404
    return jsonify({'url': url_map.original}), 200
