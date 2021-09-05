from .messages import *

__all__ = (
    'OK_BAD_MESSAGES_TRANSLATE_PACK',
)


OK_BAD_MESSAGES_TRANSLATE_PACK = {
    str(ACCESS_ERR): dict(
        default="access error",
        ru="ошибка доступа",
    ),
    str(ALREADY_USED_ERR): dict(
        default="already used",
        ru="уже используется",
    ),
    str(AUTH_ERR): dict(
        default="authorization error",
        ru="ошибка авторизации",
    ),
    str(BAD_REQUEST_ERR): dict(
        default="bad request",
        ru="некорректный запрос",
    ),
    str(DATA_ERR): dict(
        default="incorrect data",
        ru="некорректные данные",
    ),
    str(FORMAT_ERR): dict(
        default="incorrect format",
        ru="некорректный формат",
    ),
    str(NOT_AVAILABLE): dict(
        default="not available",
        ru="недоступно",
    ),
    str(NOT_EXIST_ERR): dict(
        default="existence error",
        ru="не существует",
    ),
    str(NOT_IMPLEMENTED_ERR): dict(
        default="functionality is not implemented",
        ru="функционал не реализован",
    ),
    str(OK): dict(
        default="ok",
        ru="ок",
    ),
    str(PROHIBITED_ERR): dict(
        default="prohibited",
        ru="запрещено",
    ),
    str(SERVER_ERR): dict(
        default="server error",
        ru="ошибка сервера",
    ),
    str(SIZE_ERR): dict(
        default="size error",
        ru="ошибка размера",
    ),
    str(TOO_FEW_ERR): dict(
        default="too few",
        ru="слишком мало",
    ),
    str(TOO_LONG_ERR): dict(
        default="too long",
        ru="слишком длинное значение",
    ),
    str(TOO_MUCH_ERR): dict(
        default="too much",
        ru="слишком много",
    ),
    str(TOO_SHORT_ERR): dict(
        default="too short",
        ru="слишком короткое значение",
    ),
    str(TOO_SIMPLE_ERR): dict(
        default="too simple",
        ru="слишком просто",
    ),
    str(UNKNOWN_ERR): dict(
        default="unknown error",
        ru="неизвестная ошибка",
    ),
    str(VAL_ERR): dict(
        default="incorrect value",
        ru="некорректное значение",
    ),
    str(VAL_MISSED_ERR): dict(
        default="value missed",
        ru="пропущено значение",
    ),
    str(WRONG_VAL_ERR): dict(
        default="wrong value",
        ru="неверное значение",
    ),
}
