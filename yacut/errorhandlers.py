"""Custom error handlers for the web UI and the API."""

from http import HTTPStatus

from flask import Response, jsonify, render_template, request

from yacut import app
from yacut.constants import NOT_FOUND_MESSAGE

ERROR_TEMPLATE = 'errors/error.html'
SERVER_ERROR_MESSAGE: str = 'Внутренняя ошибка сервера'
PAGE_NOT_FOUND_MESSAGE: str = 'Такой страницы нет'


def is_api_request() -> bool:
    """Check whether the current request targets the API namespace."""
    return request.path.startswith('/api/')


@app.errorhandler(HTTPStatus.NOT_FOUND)
def handle_not_found(error) -> tuple[Response, int]:
    """Render a custom page or JSON body for missing resources.

    Args:
        error: The caught HTTP exception.

    Returns:
        tuple[Response, int]: Error response with the 404 status code.
    """
    status_code = int(HTTPStatus.NOT_FOUND)
    if is_api_request():
        return jsonify({'message': NOT_FOUND_MESSAGE}), status_code
    return render_template(
        ERROR_TEMPLATE,
        code=status_code,
        message=PAGE_NOT_FOUND_MESSAGE,
    ), status_code


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def handle_server_error(error) -> tuple[Response, int]:
    """Render a custom page or JSON body for server failures.

    Args:
        error: The caught HTTP exception.

    Returns:
        tuple[Response, int]: Error response with the 500 status code.
    """
    status_code = int(HTTPStatus.INTERNAL_SERVER_ERROR)
    if is_api_request():
        return jsonify({'message': SERVER_ERROR_MESSAGE}), status_code
    return render_template(
        ERROR_TEMPLATE,
        code=status_code,
        message=SERVER_ERROR_MESSAGE,
    ), status_code
