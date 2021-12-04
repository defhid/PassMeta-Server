from App.special import Enum, loc
from typing import Dict, Type

__all__ = (
    'HistoryKind',
    'HistoryKinds',
)


class HistoryKind:
    __slots__ = ('id', 'name_loc')

    def __init__(self, kind_id: int, kind_name_loc: Dict[str, str]):
        self.id = kind_id
        self.name_loc = kind_name_loc


class HistoryKinds(Enum[HistoryKind, int]):
    @classmethod
    def init(cls) -> 'Type[HistoryKinds]':
        cls._init(HistoryKind, lambda i: i.id)
        return cls

    # region User

    USER_SIGN_IN_SUCCESS = HistoryKind(1, loc(
        default="Successful user authorization",
        ru="Успешная авторизация пользователя",
    ))
    USER_SIGN_IN_FAILURE = HistoryKind(2, loc(
        default="Failure user authorization",
        ru="Неудачная авторизация пользователя",
    ))

    USER_REGISTER_SUCCESS = HistoryKind(3, loc(
        default="Successful user sign-up",
        ru="Успешная регистрация пользователя",
    ))
    USER_REGISTER_FAILURE = HistoryKind(4, loc(
        default="Failure user sign-up",
        ru="Неудачная регистрация пользователя",
    ))

    USER_EDIT_SUCCESS = HistoryKind(5, loc(
        default="Successful user data changing",
        ru="Успешное изменение данных пользователя",
    ))
    USER_EDIT_FAILURE = HistoryKind(6, loc(
        default="Failure user data changing",
        ru="Неудачная изменение данных пользователя",
    ))

    # endregion

    # region PassFile

    GET_PASSFILE_SUCCESS = HistoryKind(7, loc(
        default="Successful passfile get",
        ru="Успешное получение файла паролей",
    ))
    GET_PASSFILE_FAILURE = HistoryKind(8, loc(
        default="Failure passfile getting",
        ru="Неудачное получение файла паролей",
    ))

    CREATE_PASSFILE_SUCCESS = HistoryKind(9, loc(
        default="Passfile success create",
        ru="Успешное создание файла паролей",
    ))

    EDIT_PASSFILE_INFO_SUCCESS = HistoryKind(10, loc(
        default="Successful passfile info changing",
        ru="Успешное изменение информации о файле паролей",
    ))
    EDIT_PASSFILE_INFO_FAILURE = HistoryKind(11, loc(
        default="Failed passfile info changing",
        ru="Неудачное изменение информации о файле паролей",
    ))

    EDIT_PASSFILE_SMTH_SUCCESS = HistoryKind(12, loc(
        default="Successful passfile changing",
        ru="Успешное изменение файла паролей",
    ))
    EDIT_PASSFILE_SMTH_FAILURE = HistoryKind(13, loc(
        default="Failed passfile changing",
        ru="Неудачное изменение файла паролей",
    ))

    ARCHIVE_PASSFILE_SUCCESS = HistoryKind(14, loc(
        default="Successful passfile archiving",
        ru="Успешное архивирование файла паролей",
    ))
    ARCHIVE_PASSFILE_FAILURE = HistoryKind(15, loc(
        default="Failure passfile archiving",
        ru="Неудачное архивирование файла паролей",
    ))

    UNARCHIVE_PASSFILE_SUCCESS = HistoryKind(16, loc(
        default="Successful passfile unarchiving",
        ru="Успешное разархивирование файла паролей",
    ))
    UNARCHIVE_PASSFILE_FAILURE = HistoryKind(17, loc(
        default="Failure passfile unarchiving",
        ru="Неудачное разархивирование файла паролей",
    ))

    DELETE_PASSFILE_SUCCESS = HistoryKind(18, loc(
        default="Successful passfile deletion",
        ru="Успешное удаление файла паролей",
    ))
    DELETE_PASSFILE_FAILURE = HistoryKind(19, loc(
        default="Failure passfile deletion",
        ru="Неудачное удаление файла паролей",
    ))

    # endregion
