"""Custom error handlers for the web UI and the API."""

from flask import Response, jsonify, render_template, request

from yacut import app
from yacut.constants import NOT_FOUND_MESSAGE

ERROR_TEMPLATE = 'errors/error.html'
SERVER_ERROR_MESSAGE: str = 'Внутренняя ошибка сервера'
PAGE_NOT_FOUND_MESSAGE: str = 'Такой страницы нет'


def is_api_request() -> bool:
    """Check whether the current request targets the API namespace."""
    return request.path.startswith('/api/')


@app.errorhandler(404)
def handle_not_found(error) -> tuple[Response, int]:
    """Render a custom page or JSON body for missing resources.

    Args:
        error: The caught HTTP exception.

    Returns:
        tuple[Response, int]: Error response with the 404 status code.
    """
    if is_api_request():
        return jsonify({'message': NOT_FOUND_MESSAGE}), 404
    return render_template(
        ERROR_TEMPLATE,
        code=404,
        message=PAGE_NOT_FOUND_MESSAGE,
    ), 404


@app.errorhandler(500)
def handle_server_error(error) -> tuple[Response, int]:
    """Render a custom page or JSON body for server failures.

    Args:
        error: The caught HTTP exception.

    Returns:
        tuple[Response, int]: Error response with the 500 status code.
    """
    if is_api_request():
        return jsonify({'message': SERVER_ERROR_MESSAGE}), 500
    return render_template(
        ERROR_TEMPLATE,
        code=500,
        message=SERVER_ERROR_MESSAGE,
    ), 500
