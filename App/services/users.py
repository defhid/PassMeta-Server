from typing import Any, Coroutine

from App.models.okbad import *
from App.services.base import DbServiceBase
from App.models.dto.requests import SignUpDto, UserPatchDto
from App.models.enums import HistoryKind
from App.database import MakeSql, User
from App.utils.crypto import CryptoUtils

__all__ = (
    'UserService',
)


class UserService(DbServiceBase):
    __slots__ = ()

    def get_user_by_id(self, user_id: int) -> Coroutine[Any, Any, User | None]:
        return self.db.query_first(User, self._SELECT_BY_ID, {'id': user_id})

    def get_user_by_login(self, user_login: str) -> Coroutine[Any, Any, User | None]:
        return self.db.query_first(User, self._SELECT_BY_LOGIN, {'login': user_login.strip()})

    async def create_user(self, data: SignUpDto) -> User:
        """ Raises Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.USER_SIGN_UP_SUCCESS,
                HistoryKind.USER_SIGN_UP_FAILURE,
        ) as history_operation:
            user = User()

            user.login = data.login
            user.full_name = data.full_name
            user.is_active = True

            result = self._validate_and_prepare_user_to_save(user, data.password)

            existing_user_id = await self.db.query_scalar(int, self._SELECT_ID_BY_LOGIN, user)
            if existing_user_id is not None:
                history_operation.with_affected_user(existing_user_id)
                if result:
                    raise Bad(VALIDATION_ERR, MORE.value_already_used(WHAT.USER.login))
                else:
                    result.more = [] if result.more is None else result.more
                    result.more.append(MORE.value_already_used(WHAT.USER.login))

            result.raise_if_failure()

            await history_operation.start_db_transaction()

            user = await self.db.query_first(User, self._INSERT, user)
            history_operation.with_affected_user(user.id)

        return user

    async def edit_user(self, user_id: int, data: UserPatchDto) -> User:
        """ Raises Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.USER_EDIT_SUCCESS,
                HistoryKind.USER_EDIT_FAILURE,
        ) as history_operation:
            user = await self.db.query_first(User, self._SELECT_BY_ID, {'id': user_id})

            history_operation.with_affected_user(user.id)

            if user.id != self.request.user_id:
                raise Bad(ACCESS_ERR, MORE.value_wrong(WHAT.USER.user_id))

            password_confirm_required = data.login is not None or data.password is not None

            if password_confirm_required:
                if data.password_confirm is None:
                    await history_operation.raise_bad(
                        Bad(VALIDATION_ERR, MORE.value_wrong(WHAT.USER.password_confirm)), "CONF MISS")

                if not CryptoUtils.check_user_password(data.password_confirm, user.pwd):
                    await history_operation.raise_bad(
                        Bad(VALIDATION_ERR, MORE.value_wrong(WHAT.USER.password_confirm)), "CONF WRONG")

            fields = ('login', 'full_name')
            for field in fields:
                val = getattr(data, field)
                if val is not None:
                    setattr(user, field, val)

            result = self._validate_and_prepare_user_to_save(user, data.password)

            user_id_by_login = await self.db.query_scalar(int, self._SELECT_ID_BY_LOGIN, user)
            if user_id_by_login is not None and user_id_by_login != user.id:
                if result:
                    result = Bad(VALIDATION_ERR, MORE.value_already_used(WHAT.USER.login))
                else:
                    result.more = [] if result.more is None else result.more
                    result.more.append(MORE.value_already_used(WHAT.USER.login))

            result.raise_if_failure()

            await history_operation.start_db_transaction()
            await self.db.query_first(User, self._UPDATE, user)

        return user

    @staticmethod
    def _validate_and_prepare_user_to_save(user: User, password: str | None) -> Result:
        errors = []
        c = User.Constrains

        user.login = user.login.strip()

        if len(user.login) < c.LOGIN_LEN_MIN:
            errors.append(MORE.value_short(WHAT.USER.login, c.LOGIN_LEN_MIN))
        if len(user.login) > c.LOGIN_LEN_MAX:
            errors.append(MORE.value_long(WHAT.USER.login, c.LOGIN_LEN_MAX))

        user.full_name = user.full_name.strip()

        if len(user.full_name) < c.FULL_NAME_LEN_MIN:
            errors.append(MORE.value_short(WHAT.USER.full_name, c.FULL_NAME_LEN_MIN))
        if len(user.full_name) > c.FULL_NAME_LEN_MAX:
            errors.append(MORE.value_long(WHAT.USER.full_name, c.FULL_NAME_LEN_MAX))

        if password is not None:
            if len(password) < c.PASSWORD_RAW_LEN_MIN:
                errors.append(MORE.value_short(WHAT.USER.password, c.PASSWORD_RAW_LEN_MIN))
            if len(password) > c.PASSWORD_RAW_LEN_MAX:
                errors.append(MORE.value_long(WHAT.USER.password, c.PASSWORD_RAW_LEN_MAX))

            user.pwd = CryptoUtils.make_user_pwd(password)

        elif not user.id:
            errors.append(MORE.value_missed(WHAT.USER.password))

        return Bad(VALIDATION_ERR, errors) if errors else Ok()

    # region SQL

    _SELECT_BY_ID = MakeSql("""SELECT * FROM users WHERE id = #id""")

    _SELECT_BY_LOGIN = MakeSql("""SELECT * FROM users WHERE login = #login""")

    _SELECT_ID_BY_LOGIN = MakeSql("""SELECT id FROM users WHERE login = #login""")

    _INSERT = MakeSql("""
        INSERT INTO users (login, pwd, full_name, is_active) 
        VALUES (#login, #pwd, #full_name, #is_active)
        RETURNING *
    """)

    _UPDATE = MakeSql("""
        UPDATE users SET (login, full_name, pwd) = (#login, #full_name, #pwd)
        WHERE id = #id
        RETURNING *
    """)

    # endregion
