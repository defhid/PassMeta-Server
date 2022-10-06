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
        default="Successful user authorization",
        ru="Успешная авторизация пользователя",
    ),
    HistoryKind.USER_SIGN_IN_FAILURE: loc(
        default="Failure user authorization",
        ru="Неудачная авторизация пользователя",
    ),
    HistoryKind.USER_REGISTER_SUCCESS: loc(
        default="Successful user sign-up",
        ru="Успешная регистрация пользователя",
    ),
    HistoryKind.USER_REGISTER_FAILURE: loc(
        default="Failure user sign-up",
        ru="Неудачная регистрация пользователя",
    ),
    HistoryKind.USER_EDIT_SUCCESS: loc(
        default="Successful user data changing",
        ru="Успешное изменение данных пользователя",
    ),
    HistoryKind.USER_EDIT_FAILURE: loc(
        default="Failure user data changing",
        ru="Неудачная изменение данных пользователя",
    ),
    HistoryKind.GET_PASSFILE_SUCCESS: loc(
        default="Successful passfile get",
        ru="Успешное получение файла паролей",
    ),
    HistoryKind.GET_PASSFILE_FAILURE: loc(
        default="Failure passfile getting",
        ru="Неудачное получение файла паролей",
    ),
    HistoryKind.CREATE_PASSFILE_SUCCESS: loc(
        default="Successful passfile creation",
        ru="Успешное создание файла паролей",
    ),
    HistoryKind.CREATE_PASSFILE_FAILURE: loc(
        default="Failed passfile creation",
        ru="Неудачное создание файла паролей",
    ),
    HistoryKind.EDIT_PASSFILE_INFO_SUCCESS: loc(
        default="Successful passfile info changing",
        ru="Успешное изменение информации о файле паролей",
    ),
    HistoryKind.EDIT_PASSFILE_INFO_FAILURE: loc(
        default="Failed passfile info changing",
        ru="Неудачное изменение информации о файле паролей",
    ),
    HistoryKind.EDIT_PASSFILE_SMTH_SUCCESS: loc(
        default="Successful passfile changing",
        ru="Успешное изменение файла паролей",
    ),
    HistoryKind.EDIT_PASSFILE_SMTH_FAILURE: loc(
        default="Failed passfile changing",
        ru="Неудачное изменение файла паролей",
    ),
    HistoryKind.DELETE_PASSFILE_SUCCESS: loc(
        default="Successful passfile deletion",
        ru="Успешное удаление файла паролей",
    ),
    HistoryKind.DELETE_PASSFILE_FAILURE: loc(
        default="Failure passfile deletion",
        ru="Неудачное удаление файла паролей",
    ),
}
