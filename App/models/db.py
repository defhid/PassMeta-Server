from App.special import *
from App.models.extra import *
from App.utils.db import db_model_base as DbModelBase
from App.utils.passfile import PassFileUtils
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
    user_id = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    data: bytes

    @property
    def path(self) -> str:
        if self.is_archived:
            return PassFileUtils.make_filepath_archived(self.id)
        return PassFileUtils.make_filepath_normal(self.id, self.user_id)

    @property
    def archive_path(self) -> str:
        return PassFileUtils.make_filepath_archived(self.id)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'id': self.id,
            'created_on': self.created_on,
            'changed_on': self.changed_on,
            'is_archived': self.is_archived,
            'data': self.data if hasattr(self, 'data') else None,
        }
        return d


class History(DbModelBase):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kind_id = Column(SmallInteger, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    class Kind(Enum[HistoryKind]):
        USER_SIGN_IN_SUCCESS = HistoryKind(1, "Успешная авторизация пользователя")
        USER_SIGN_IN_FAILURE = HistoryKind(2, "Неудачная авторизация пользователя")

        USER_REGISTER_SUCCESS = HistoryKind(3, "Успешная регистрация пользователя")
        USER_REGISTER_FAILURE = HistoryKind(4, "Неудачная регистрация пользователя")

        USER_EDIT_SUCCESS = HistoryKind(3, "Успешное изменение данных пользователя")
        USER_EDIT_FAILURE = HistoryKind(4, "Неудачная изменение данных пользователя")

        GET_PASSFILE_SUCCESS = HistoryKind(5, "Успешное получение файла паролей")
        GET_PASSFILE_FAILURE = HistoryKind(6, "Неудачное получение файла паролей")

        SET_PASSFILE_SUCCESS = HistoryKind(7, "Успешное создание/изменение файла паролей")
        SET_PASSFILE_FAILURE = HistoryKind(8, "Неудачное создание/изменение файла паролей")

        DELETE_PASSFILE_SUCCESS = HistoryKind(9, "Успешное удаление файла паролей")
        DELETE_PASSFILE_FAILURE = HistoryKind(10, "Неудачное удаление файла паролей")

    Kind.init()


class HistoryMore(DbModelBase):
    __tablename__ = "history_more"

    id = Column(Integer, primary_key=True, autoincrement=True)
    history_id = Column(Integer, ForeignKey("history.id"), nullable=True)
    info = Column(String(256))
