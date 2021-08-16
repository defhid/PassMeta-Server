from App.special import *
from App.models.extra import *
from App.utils.db import db_model_base as DbModelBase
from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey, Boolean
from uuid import uuid4
from typing import Any, Dict

__all__ = (
    'User',
    'Session',
    'PassFile',
    'Log',
    'LogMore',
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


class Log(DbModelBase):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kind_id = Column(SmallInteger, nullable=False)
    entity_id = Column(Integer, nullable=True)
    when = Column(DateTime, default=datetime.utcnow, nullable=False)

    class Kind(Enum[LogKind]):
        USER_SIGN_IN_SUCCESS = LogKind(1, "Успешная авторизация пользователя", User)
        USER_SIGN_IN_FAILURE = LogKind(2, "Неудачная авторизация пользователя", None)

        USER_REGISTER_SUCCESS = LogKind(3, "Успешная регистрация пользователя", User)
        USER_REGISTER_FAILURE = LogKind(4, "Неудачная регистрация пользователя", None)

        USER_EDIT_SUCCESS = LogKind(3, "Успешное изменение данных пользователя", User)
        USER_EDIT_FAILURE = LogKind(4, "Неудачная изменение данных пользователя", None)

        GET_PASSFILE_SUCCESS = LogKind(5, "Успешное получение файла паролей", User)
        GET_PASSFILE_FAILURE = LogKind(6, "Неудачное получение файла паролей", User)

        SET_PASSFILE_SUCCESS = LogKind(5, "Успешное создание/изменение файла паролей", PassFile)
        SET_PASSFILE_FAILURE = LogKind(6, "Неудачное создание/изменение файла паролей", PassFile)

        DELETE_PASSFILE_SUCCESS = LogKind(5, "Успешное удаление файла паролей", PassFile)
        DELETE_PASSFILE_FAILURE = LogKind(6, "Неудачное удаление файла паролей", PassFile)

    Kind.init()


class LogMore(DbModelBase):
    __tablename__ = "logs_more"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(Integer, ForeignKey("logs.id"), nullable=True)
    info = Column(String(256))
