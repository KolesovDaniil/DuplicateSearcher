"""хэндлеры для обработки общих исключений"""

from http import HTTPStatus

from app.exceptions import NotFoundError, ForbiddenError
from app.namespaces import ErrorNs


@ErrorNs.ns.errorhandler(NotFoundError)
@ErrorNs.ns.marshal_with(ErrorNs.error_model, code=HTTPStatus.NOT_FOUND)
def not_found_error_handler(e):
    """Обработчик для ошибок не найденного ресурса"""
    return {'message': e}, HTTPStatus.NOT_FOUND


@ErrorNs.ns.errorhandler(ForbiddenError)
@ErrorNs.ns.marshal_with(ErrorNs.error_model, code=HTTPStatus.FORBIDDEN)
def forbidden_error_handler(e):
    """Обработчик ошибок отказа доступа"""
    return {'message': e}, HTTPStatus.FORBIDDEN
