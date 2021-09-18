from App.special import *
from App.models.extra import *
from App.utils.db import DbModelBase
from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey, Boolean
from uuid import uuid4
from typing import Any, Dict

__all__ = (
    'User',
    'Session',
    'PassFile',
    'History',
    'HistoryMore',
    'DbModelBase',
)


class User(DbModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(150), unique=True, nullable=False)
    pwd = Column(String(128), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    is_active = Column(Boolean, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'login': self.login,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
        }


class Session(DbModelBase):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)


class PassFile(DbModelBase):
    __tablename__ = "passfile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    def to_dict(self, data: bytes = None) -> Dict[str, Any]:
        d = {
            'id': self.id,
            'name': self.name,
            'created_on': str(self.created_on),
            'changed_on': str(self.changed_on),
            'version': self.version,
            'is_archived': self.is_archived,
            'smth': None if data is None else data.decode('utf-8'),
        }
        return d


class History(DbModelBase):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kind_id = Column(SmallInteger, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    class Kind(Enum[HistoryKind]):
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

        EDIT_PASSFILE_SUCCESS = HistoryKind(10, loc(
            default="Successful passfile changing",
            ru="Успешное изменение файла паролей",
        ))
        EDIT_PASSFILE_FAILURE = HistoryKind(11, loc(
            default="Failed passfile changing",
            ru="Неудачное изменение файла паролей",
        ))

        ARCHIVE_PASSFILE_SUCCESS = HistoryKind(12, loc(
            default="Successful passfile archiving",
            ru="Успешное архивирование файла паролей",
        ))
        ARCHIVE_PASSFILE_FAILURE = HistoryKind(13, loc(
            default="Failure passfile archiving",
            ru="Неудачное архивирование файла паролей",
        ))

        UNARCHIVE_PASSFILE_SUCCESS = HistoryKind(14, loc(
            default="Successful passfile unarchiving",
            ru="Успешное разархивирование файла паролей",
        ))
        UNARCHIVE_PASSFILE_FAILURE = HistoryKind(15, loc(
            default="Failure passfile unarchiving",
            ru="Неудачное разархивирование файла паролей",
        ))

        DELETE_PASSFILE_SUCCESS = HistoryKind(16, loc(
            default="Successful passfile deletion",
            ru="Успешное удаление файла паролей",
        ))
        DELETE_PASSFILE_FAILURE = HistoryKind(17, loc(
            default="Failure passfile deletion",
            ru="Неудачное удаление файла паролей",
        ))

    Kind.init()


class HistoryMore(DbModelBase):
    __tablename__ = "history_more"

    id = Column(Integer, primary_key=True, autoincrement=True)
    history_id = Column(Integer, ForeignKey("history.id"), nullable=True)
    info = Column(String(256))
