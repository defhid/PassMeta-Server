from typing import Coroutine

from App.services.base import DbServiceBase
from App.special import *

from App.models.dto import SignUpDto, UserPatchDto
from App.models.entities import RequestInfo
from App.models.enums import HistoryKind

from App.database import MakeSql, User
from App.utils.crypto import CryptoUtils

__all__ = (
    'UserService',
)


class UserService(DbServiceBase):
    __slots__ = ()

    def get_user_by_id(self, user_id: int) -> Coroutine[Any, Any, Optional[User]]:
        return self.db.query_first(User, self._SELECT_BY_ID, {'id': user_id})

    def get_user_by_login(self, user_login: str) -> Coroutine[Any, Any, Optional[User]]:
        return self.db.query_first(User, self._SELECT_BY_LOGIN, {'login': user_login.strip()})

    async def create_user(self, data: SignUpDto) -> User:
        """ Raises DATA_ERR, ALREADY_USED_ERR.
        """
        user = User()

        user.login = data.login
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.is_active = True

        result = self._validate_and_prepare_user_to_save(user, data.password)

        existing_user_id = await self.db.query_scalar(int, self._SELECT_ID_BY_LOGIN, user)
        if existing_user_id is not None:
            await self.history_writer.write(HistoryKind.USER_REGISTER_FAILURE,
                                            None, existing_user_id, None, "LOGIN")
            if result.success:
                raise Bad('login', ALREADY_USED_ERR)
            else:
                result.sub.append(Bad('login', ALREADY_USED_ERR))

        result.raise_if_failure()

        async with self.db.transaction():
            user = await self.db.query_first(User, self._INSERT, user)

            await self.history_writer.write(HistoryKind.USER_REGISTER_SUCCESS,
                                            user.id, user.id, None)

        return user

    async def edit_user(self, user_id: int, data: UserPatchDto, request: RequestInfo) -> User:
        """ Raises DATA_ERR, VAL_MISSED_ERR, ALREADY_USED_ERR.
        """
        user = await self.db.query_first(User, self._SELECT_BY_ID, {'id': user_id})

        if user.id != request.user_id:
            raise Bad(None, NOT_IMPLEMENTED_ERR)

        if data.password_confirm is None:
            await self.history_writer.write(HistoryKind.USER_EDIT_FAILURE,
                                            request.user_id, user.id, None, "CONF MISS")
            raise Bad('password_confirm', VAL_MISSED_ERR)

        if not CryptoUtils.check_user_password(data.password_confirm, user.pwd):
            await self.history_writer.write(HistoryKind.USER_EDIT_FAILURE,
                                            request.user_id, user.id, None, "CONF WRONG")
            raise Bad('password_confirm', WRONG_VAL_ERR)

        fields = ('login', 'first_name', 'last_name')
        for f in fields:
            if getattr(data, f) is not None:
                setattr(user, f, getattr(data, f))

        result = self._validate_and_prepare_user_to_save(user, data.password)

        user_id_by_login = await self.db.query_scalar(int, self._SELECT_ID_BY_LOGIN, user)
        if user_id_by_login is not None and user_id_by_login != user.id:
            if result.success:
                raise Bad('login', ALREADY_USED_ERR)
            else:
                result.sub.append(Bad('login', ALREADY_USED_ERR))

        result.raise_if_failure()

        async with self.db.transaction():
            await self.db.query_first(User, self._UPDATE, user)

            await self.history_writer.write(HistoryKind.USER_EDIT_SUCCESS,
                                            request.user_id, user.id, None)

        return user

    @staticmethod
    def _validate_and_prepare_user_to_save(user: User, password: Optional[str]) -> Result:
        errors = []
        c = User.Constrains

        user.login = user.login.strip()

        if len(user.login) < c.LOGIN_LEN_MIN:
            errors.append(Bad('login', TOO_SHORT_ERR, MORE.min_allowed(c.LOGIN_LEN_MIN)))
        if len(user.login) > c.LOGIN_LEN_MAX:
            errors.append(Bad('login', TOO_LONG_ERR, MORE.max_allowed(c.LOGIN_LEN_MAX)))

        user.first_name = user.first_name.strip()

        if len(user.first_name) < c.FIRST_NAME_LEN_MIN:
            errors.append(Bad('first_name', TOO_SHORT_ERR, MORE.min_allowed(c.FIRST_NAME_LEN_MIN)))
        if len(user.first_name) > c.FIRST_NAME_LEN_MAX:
            errors.append(Bad('first_name', TOO_LONG_ERR, MORE.max_allowed(c.FIRST_NAME_LEN_MAX)))

        user.last_name = user.last_name.strip()

        if len(user.last_name) < c.LAST_NAME_LEN_MIN:
            errors.append(Bad('last_name', TOO_SHORT_ERR, MORE.min_allowed(c.LAST_NAME_LEN_MIN)))
        if len(user.last_name) > c.LAST_NAME_LEN_MAX:
            errors.append(Bad('last_name', TOO_LONG_ERR, MORE.max_allowed(c.LAST_NAME_LEN_MAX)))

        if password is not None:
            if len(password) < c.Raw.PASSWORD_LEN_MIN:
                errors.append(Bad('password', TOO_SHORT_ERR, MORE.min_allowed(c.Raw.PASSWORD_LEN_MIN)))
            if len(password) > c.Raw.PASSWORD_LEN_MAX:
                errors.append(Bad('password', TOO_LONG_ERR, MORE.max_allowed(c.Raw.PASSWORD_LEN_MAX)))

            user.pwd = CryptoUtils.make_user_pwd(password)

        elif not user.id:
            errors.append(Bad('password', VAL_MISSED_ERR))

        return Bad(None, DATA_ERR, sub=errors) if errors else Ok()

    # region SQL

    _SELECT_BY_ID = MakeSql("""SELECT * FROM users WHERE id = #id""")

    _SELECT_BY_LOGIN = MakeSql("""SELECT * FROM users WHERE login = #login""")

    _SELECT_ID_BY_LOGIN = MakeSql("""SELECT id FROM users WHERE login = #login""")

    _INSERT = MakeSql("""
        INSERT INTO users (login, pwd, first_name, last_name, is_active) 
        VALUES (#login, #pwd, #first_name, #last_name, #is_active)
        RETURNING *
    """)

    _UPDATE = MakeSql("""
        UPDATE users SET ( login,  first_name,  last_name,  pwd)
                      = (#login, #first_name, #last_name, #pwd)
        WHERE id = #id
        RETURNING *
    """)

    # endregion
