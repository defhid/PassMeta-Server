from App.translate.helpers import loc
from App.models.enums import HistoryKind
import App.special.ok_bad.more_type as more
import App.special.ok_bad.result_code as result

__all__ = (
    'OK_BAD_MESSAGES_TRANSLATE_PACK',
    'OK_BAD_MORE_TYPES_TRANSLATE_PACK',
    'HISTORY_KINDS_TRANSLATE_PACK',
)


OK_BAD_MESSAGES_TRANSLATE_PACK = {
    result.ACCESS_ERR: loc(
        default="access error",
        ru="ошибка доступа",
    ),
    result.ALREADY_USED_ERR: loc(
        default="already used",
        ru="уже используется",
    ),
    result.AUTH_ERR: loc(
        default="authorization error",
        ru="ошибка авторизации",
    ),
    result.BAD_REQUEST_ERR: loc(
        default="bad request",
        ru="некорректный запрос",
    ),
    result.DATA_ERR: loc(
        default="incorrect data",
        ru="некорректные данные",
    ),
    result.FORMAT_ERR: loc(
        default="incorrect format",
        ru="некорректный формат",
    ),
    result.FROZEN_ERR: loc(
        default="frozen (not active)",
        ru="заблокирован (не активен)"
    ),
    result.INVALID_OPERATION_ERR: loc(
        default="invalid operation",
        ru="недопустимая операция"
    ),
    result.NOT_AVAILABLE: loc(
        default="not available",
        ru="недоступно",
    ),
    result.NOT_EXIST_ERR: loc(
        default="existence error",
        ru="не существует",
    ),
    result.NOT_IMPLEMENTED_ERR: loc(
        default="functionality is not implemented",
        ru="функционал не реализован",
    ),
    result.OK: loc(
        default="ok",
        ru="ок",
    ),
    result.PROHIBITED_ERR: loc(
        default="prohibited",
        ru="запрещено",
    ),
    result.SERVER_ERR: loc(
        default="server error",
        ru="ошибка сервера",
    ),
    result.SIZE_ERR: loc(
        default="size error",
        ru="ошибка размера",
    ),
    result.TOO_FEW_ERR: loc(
        default="too few",
        ru="слишком мало",
    ),
    result.TOO_LONG_ERR: loc(
        default="too long",
        ru="слишком длинное значение",
    ),
    result.TOO_MUCH_ERR: loc(
        default="too much",
        ru="слишком много",
    ),
    result.TOO_SHORT_ERR: loc(
        default="too short",
        ru="слишком короткое значение",
    ),
    result.TOO_SIMPLE_ERR: loc(
        default="too simple",
        ru="слишком просто",
    ),
    result.UNKNOWN_ERR: loc(
        default="unknown error",
        ru="неизвестная ошибка",
    ),
    result.VAL_ERR: loc(
        default="incorrect value",
        ru="некорректное значение",
    ),
    result.VAL_MISSED_ERR: loc(
        default="value missed",
        ru="пропущено значение",
    ),
    result.WRONG_VAL_ERR: loc(
        default="wrong value",
        ru="неверное значение",
    ),
}


OK_BAD_MORE_TYPES_TRANSLATE_PACK = {
    more.REQUIRED: loc(
        default="Required",
        ru="Требуется",
    ),
    more.ALLOWED: loc(
        default="Allowed",
        ru="Разрешено",
    ),
    more.DISALLOWED: loc(
        default="Disallowed",
        ru="Запрещено",
    ),
    more.MIN_ALLOWED: loc(
        default="Min allowed",
        ru="Разрешено (мин.)",
    ),
    more.MAX_ALLOWED: loc(
        default="Max allowed",
        ru="Разрешено (макс.)",
    )
}


HISTORY_KINDS_TRANSLATE_PACK = {
    HistoryKind.USER_SIGN_IN_SUCCESS: loc(
        default="User: authorization",
        ru="Пользователь: авторизация",
    ),
    HistoryKind.USER_SIGN_IN_FAILURE: loc(
        default="User: failed authorization",
        ru="Пользователь: неудачная авторизация",
    ),
    HistoryKind.USER_SIGN_UP_SUCCESS: loc(
        default="User: sign-up",
        ru="Пользователь: регистрация",
    ),
    HistoryKind.USER_SIGN_UP_FAILURE: loc(
        default="User: failed sign-up",
        ru="Пользователь: неудачная регистрация",
    ),
    HistoryKind.USER_SESSIONS_RESET: loc(
        default="User: reset auth",
        ru="Пользователь: сброс авторизации",
    ),
    HistoryKind.USER_EDIT_SUCCESS: loc(
        default="User: account changing",
        ru="Пользователь: изменение учётной записи",
    ),
    HistoryKind.USER_EDIT_FAILURE: loc(
        default="User: failed account changing",
        ru="Пользователь: неудачное изменение учётной записи",
    ),
    HistoryKind.GET_PASSFILE_SUCCESS: loc(
        default="Passfile: getting",
        ru="Пакет: получение",
    ),
    HistoryKind.GET_PASSFILE_FAILURE: loc(
        default="Passfile: failure getting",
        ru="Пакет: неудачное получение",
    ),
    HistoryKind.CREATE_PASSFILE_SUCCESS: loc(
        default="Passfile: creation",
        ru="Пакет: создание",
    ),
    HistoryKind.CREATE_PASSFILE_FAILURE: loc(
        default="Passfile: failed creation",
        ru="Пакет: неудачное создание",
    ),
    HistoryKind.EDIT_PASSFILE_INFO_SUCCESS: loc(
        default="Passfile: info changing",
        ru="Пакет: изменение информации",
    ),
    HistoryKind.EDIT_PASSFILE_INFO_FAILURE: loc(
        default="Passfile: failed info changing",
        ru="Пакет: неудачное изменение информации",
    ),
    HistoryKind.EDIT_PASSFILE_SMTH_SUCCESS: loc(
        default="Passfile: content changing",
        ru="Пакет: изменение содержимого",
    ),
    HistoryKind.EDIT_PASSFILE_SMTH_FAILURE: loc(
        default="Passfile: failed content changing",
        ru="Пакет: неудачное изменение содержимого",
    ),
    HistoryKind.DELETE_PASSFILE_SUCCESS: loc(
        default="Passfile: deletion",
        ru="Пакет: удаление",
    ),
    HistoryKind.DELETE_PASSFILE_FAILURE: loc(
        default="Passfile: failure deletion",
        ru="Пакет: неудачное удаление",
    ),
}
