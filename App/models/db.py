from App.special import *
from App.models.extra import *
from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

__all__ = (
    'User',
    'Log',
    'LogMore',
    'Session',
    'DbModelBase',
)

DbModelBase = declarative_base()


class User(DbModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(150), nullable=False)
    pwd = Column(String(128), nullable=False)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)


class Log(DbModelBase):
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


class LogMore(DbModelBase):
    __tablename__ = "logs_more"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(Integer, ForeignKey("logs.id"), nullable=True)
    info = Column(String(256))


class Session(DbModelBase):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=uuid4())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
