from .messages import *
from ..funcs import loc

__all__ = (
    'OK_BAD_MESSAGES_TRANSLATE_PACK',
)


OK_BAD_MESSAGES_TRANSLATE_PACK = {
    str(ACCESS_ERR): loc(
        default="access error",
        ru="ошибка доступа",
    ),
    str(ALREADY_USED_ERR): loc(
        default="already used",
        ru="уже используется",
    ),
    str(AUTH_ERR): loc(
        default="authorization error",
        ru="ошибка авторизации",
    ),
    str(BAD_REQUEST_ERR): loc(
        default="bad request",
        ru="некорректный запрос",
    ),
    str(DATA_ERR): loc(
        default="incorrect data",
        ru="некорректные данные",
    ),
    str(FORMAT_ERR): loc(
        default="incorrect format",
        ru="некорректный формат",
    ),
    str(FROZEN_ERR): loc(
        default="frozen (not active)",
        ru="заблокирован (не активен)"
    ),
    str(INVALID_OPERATION_ERR): loc(
        default="invalid operation",
        ru="недопустимая операция"
    ),
    str(NOT_AVAILABLE): loc(
        default="not available",
        ru="недоступно",
    ),
    str(NOT_EXIST_ERR): loc(
        default="existence error",
        ru="не существует",
    ),
    str(NOT_IMPLEMENTED_ERR): loc(
        default="functionality is not implemented",
        ru="функционал не реализован",
    ),
    str(OK): loc(
        default="ok",
        ru="ок",
    ),
    str(PROHIBITED_ERR): loc(
        default="prohibited",
        ru="запрещено",
    ),
    str(SERVER_ERR): loc(
        default="server error",
        ru="ошибка сервера",
    ),
    str(SIZE_ERR): loc(
        default="size error",
        ru="ошибка размера",
    ),
    str(TOO_FEW_ERR): loc(
        default="too few",
        ru="слишком мало",
    ),
    str(TOO_LONG_ERR): loc(
        default="too long",
        ru="слишком длинное значение",
    ),
    str(TOO_MUCH_ERR): loc(
        default="too much",
        ru="слишком много",
    ),
    str(TOO_SHORT_ERR): loc(
        default="too short",
        ru="слишком короткое значение",
    ),
    str(TOO_SIMPLE_ERR): loc(
        default="too simple",
        ru="слишком просто",
    ),
    str(UNKNOWN_ERR): loc(
        default="unknown error",
        ru="неизвестная ошибка",
    ),
    str(VAL_ERR): loc(
        default="incorrect value",
        ru="некорректное значение",
    ),
    str(VAL_MISSED_ERR): loc(
        default="value missed",
        ru="пропущено значение",
    ),
    str(WRONG_VAL_ERR): loc(
        default="wrong value",
        ru="неверное значение",
    ),
}
