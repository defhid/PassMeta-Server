__all__ = (
    'OK_BAD_TRANSLATE_PACK',
    'OK_BAD_MORE_TRANSLATE_PACK',
    'OK_BAD_MORE_WHAT_TRANSLATE_PACK',
    'HISTORY_KINDS_TRANSLATE_PACK',
)

from App.translate.helpers import loc
from App.models.enums import HistoryKind
from App.models.okbad.result_more_what import WHAT
import App.models.okbad.result_more_code as more
import App.models.okbad.result_code as result


OK_BAD_TRANSLATE_PACK = {
    result.ACCESS_ERR: loc(
        default="access error",
        ru="ошибка доступа",
    ),
    result.AUTH_ERR: loc(
        default="authorization error",
        ru="ошибка авторизации",
    ),
    result.VALIDATION_ERR: loc(
        default="incorrect data",
        ru="некорректные данные",
    ),
    result.UNPROCESSABLE_ERR: loc(
        default="cannot handle request",
        ru="невозможно обработать запрос",
    ),
    result.OK: loc(
        default="ok",
        ru="ок",
    ),
    result.SERVER_ERR: loc(
        default="server error",
        ru="ошибка сервера",
    ),
}


OK_BAD_MORE_TRANSLATE_PACK = {
    more.VALUE_FEW: loc(
        default="too few, minimum is {0}",
        ru="слишком мало, минимум {0}",
    ),
    more.VALUE_MUCH: loc(
        default="too much, maximum is {0}",
        ru="слишком много, максимум {0",
    ),
    more.VALUE_SHORT: loc(
        default="too short, minimum is {0}",
        ru="слишком короткое значение, минимум {0}",
    ),
    more.VALUE_LONG: loc(
        default="too long, maximum is {0}",
        ru="слишком длинное значение, максимум {0}",
    ),
    more.VALUE_MISSED: loc(
        default="missed value",
        ru="значение пропущено",
    ),
    more.VALUE_WRONG: loc(
        default="wrong value",
        ru="значение неверное",
    ),
    more.VALUE_ALREADY_USED: loc(
        default="value is already used",
        ru="значение уже используется",
    ),
    more.FORMAT_WRONG: loc(
        default="wrong format, required '{0}'",
        ru="неверный формат, требуется '{0}'",
    ),
    more.FROZEN: loc(
        default="frozen (not active)",
        ru="заблокирован (не активен)"
    ),
    more.NOT_FOUND: loc(
        default="not found",
        ru="не найден",
    ),
}


OK_BAD_MORE_WHAT_TRANSLATE_PACK = {
    WHAT.USER.user_id: loc(
        default="user id",
        ru="id пользователя",
    ),
    WHAT.USER.user: loc(
        default="user",
        ru="пользователь",
    ),
    WHAT.USER.login: loc(
        default="login",
        ru="логин",
    ),
    WHAT.USER.full_name: loc(
        default="name",
        ru="Имя",
    ),
    WHAT.USER.password: loc(
        default="password",
        ru="пароль",
    ),
    WHAT.USER.password_confirm: loc(
        default="password confirmation",
        ru="подтверждение пароля",
    ),

    WHAT.PASSFILE.passfile_id: loc(
        default="passfile id",
        ru="id пакета паролей",
    ),
    WHAT.PASSFILE.version: loc(
        default="version",
        ru="версия",
    ),
    WHAT.PASSFILE.name: loc(
        default="name",
        ru="название",
    ),
    WHAT.PASSFILE.color: loc(
        default="color",
        ru="цвет",
    ),
    WHAT.PASSFILE.created_on: loc(
        default="creation date",
        ru="дата создания",
    ),

    WHAT.HISTORY.kind: loc(
        default="kind",
        ru="вид",
    ),
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
    HistoryKind.GET_PASSFILE_LIST_SUCCESS: loc(
        default="Passfile: info list getting",
        ru="Пакет: получение списка информации",
    ),
    HistoryKind.GET_PASSFILE_LIST_FAILURE: loc(
        default="Passfile: failed info list getting",
        ru="Пакет: неудачное получение списка информации",
    ),
    HistoryKind.GET_PASSFILE_INFO_SUCCESS: loc(
        default="Passfile: info getting",
        ru="Пакет: получение информации",
    ),
    HistoryKind.GET_PASSFILE_INFO_FAILURE: loc(
        default="Passfile: failed info getting",
        ru="Пакет: неудачное получение информации",
    ),
    HistoryKind.GET_PASSFILE_SMTH_SUCCESS: loc(
        default="Passfile: content getting",
        ru="Пакет: получение содержимого",
    ),
    HistoryKind.GET_PASSFILE_SMTH_FAILURE: loc(
        default="Passfile: failed content getting",
        ru="Пакет: неудачное получение содержимого",
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
        default="Passfile: failed deletion",
        ru="Пакет: неудачное удаление",
    ),
}
