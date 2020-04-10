"""хэндлеры для обработки общих исключений"""

from http import HTTPStatus

from app.exceptions import NotFoundError
from app.namespaces import ErrorNs


@ErrorNs.ns.error_handlers(NotFoundError)
@ErrorNs.ns.marshal_with(ErrorNs.error_model, code=HTTPStatus.NOT_FOUND)
def not_found_error(e):
    """Обработчик для ошибок не найденного ресурса"""
    return {'message': e}, HTTPStatus.NOT_FOUND