from .messages import *

__all__ = (
    'OK_BAD_MESSAGES_TRANSLATE_PACK',
)


OK_BAD_MESSAGES_TRANSLATE_PACK = {
    str(ACCESS_ERR): dict(
        rus="ошибка доступа",
        en="access error",
    ),
    str(ALREADY_USED_ERR): dict(
        rus="уже используется",
        en="already used",
    ),
    str(AUTH_ERR): dict(
        rus="ошибка авторизации",
        en="authorization error",
    ),
    str(BAD_REQUEST_ERR): dict(
        rus="некорректный запрос",
        en="bad request",
    ),
    str(DATA_ERR): dict(
        rus="некорректные данные",
        en="incorrect data",
    ),
    str(FORMAT_ERR): dict(
        rus="некорректный формат",
        en="incorrect format",
    ),
    str(NOT_AVAILABLE): dict(
        rus="недоступно",
        en="not available",
    ),
    str(NOT_EXIST_ERR): dict(
        rus="не существует",
        en="existence error",
    ),
    str(NOT_IMPLEMENTED_ERR): dict(
        rus="функционал не реализован",
        en="functionality is not implemented",
    ),
    str(OK): dict(
        rus="ок",
        en="ok",
    ),
    str(PROHIBITED_ERR): dict(
        rus="запрещено",
        en="prohibited",
    ),
    str(SERVER_ERR): dict(
        rus="ошибка сервера",
        en="server error",
    ),
    str(SIZE_ERR): dict(
        rus="ошибка размера",
        en="size error",
    ),
    str(TOO_FEW_ERR): dict(
        rus="слишком мало",
        en="too few",
    ),
    str(TOO_LONG_ERR): dict(
        rus="слишком длинный",
        en="too long",
    ),
    str(TOO_MUCH_ERR): dict(
        rus="слишком много",
        en="too much",
    ),
    str(TOO_SHORT_ERR): dict(
        rus="слишком коротко",
        en="too short",
    ),
    str(TOO_SIMPLE_ERR): dict(
        rus="слишком просто",
        en="too simple",
    ),
    str(UNKNOWN_ERR): dict(
        rus="неизвестная ошибка",
        en="unknown error",
    ),
    str(VAL_ERR): dict(
        rus="некорректное значение",
        en="incorrect value",
    ),
    str(VAL_MISSED_ERR): dict(
        rus="пропущено значение",
        en="value missed",
    ),
    str(WRONG_VAL_ERR): dict(
        rus="неверное значение",
        en="wrong value",
    ),
}
