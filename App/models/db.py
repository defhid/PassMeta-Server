from App.special import *
from App.models.extra import *
from App.utils.db import *
from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey
from uuid import uuid4
from typing import Any, Dict

__all__ = (
    'User',
    'Log',
    'LogMore',
    'Session',
    'db_model_base',
)


class User(db_model_base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(150), nullable=False)
    pwd = Column(String(128), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'login': self.login,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


class Log(db_model_base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kind_id = Column(SmallInteger, nullable=False)
    entity_id = Column(Integer, nullable=False)
    when = Column(DateTime, default=datetime.utcnow, nullable=False)

    class Kind(Enum[LogKind]):
        USER_SIGN_IN_SUCCESS = LogKind(1, "Успешная авторизация пользователя")
        USER_SIGN_IN_FAILURE = LogKind(2, "Неудачная авторизация пользователя")

        USER_SIGN_UP_SUCCESS = LogKind(3, "Успешная регистрация пользователя")
        USER_SIGN_UP_FAILURE = LogKind(4, "Неудачная регистрация пользователя")

        GET_PASSFILE_SUCCESS = LogKind(5, "Успешное получение файла паролей")
        GET_PASSFILE_FAILURE = LogKind(6, "Успешное получение файла паролей")

    Kind.init()


class LogMore(db_model_base):
    __tablename__ = "logs_more"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(Integer, ForeignKey("logs.id"), nullable=True)
    info = Column(String(256))


class Session(db_model_base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
