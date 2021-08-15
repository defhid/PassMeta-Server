class ResMessage(str):
    __slots__ = ('rus', 'response_status_code')
    rus: str
    response_status_code: int

    def __init__(self, _, rus: str, response_status_code=200):
        s = super()
        s.__setattr__('rus', rus)
        s.__setattr__('response_status_code', response_status_code)

    def __new__(cls, message: str, *args, **kwargs):
        obj = str.__new__(cls, message)
        return obj

    def __repr__(self):
        return f"<ResMessage '{self}', {self.response_status_code}>"

    def __setattr__(self, key, value):
        raise TypeError(f"{type(self).__name__} object is immutable!")

    def __delattr__(self, item):
        raise TypeError(f"{type(self).__name__} object is immutable!")

    def to(self, locale):
        if locale == "ru":
            return self.rus
        return self


ACCESS_ERR = ResMessage(
    "ACCESS ERROR",
    "Ошибка доступа!",
    403
)

ALREADY_USED_ERR = ResMessage(
    "ALREADY USED",
    "Уже используется!"
)

AUTH_ERR = ResMessage(
    "AUTH ERROR",
    "Не авторизован!",
    401
)

BAD_REQUEST_ERR = ResMessage(
    "BAD REQUEST",
    "Некорректный запрос!",
    400
)

DATA_ERR = ResMessage(
    "INVALID DATA",
    "Неверные данные!"
)

FORMAT_ERR = ResMessage(
    "INCORRECT FORMAT",
    "Неверный формат!"
)

NOT_AVAILABLE = ResMessage(
    "NOT AVAILABLE",
    "Ресурс недоступен!"
)

NOT_EXIST_ERR = ResMessage(
    "NOT EXIST",
    "Не существует!"
)

OK = ResMessage(
    "OK",
    "Ок"
)

PROHIBITED_ERR = ResMessage(
    "PROHIBITED",
    "Запрещено!"
)

SERVER_ERR = ResMessage(
    "SERVER ERROR",
    "Ошибка сервера!",
    500
)

SIZE_ERR = ResMessage(
    "SIZE ERROR",
    "Ошибка размера!"
)

TOO_FEW_ERR = ResMessage(
    "TOO FEW",
    "Слишком мало!"
)

TOO_LONG_ERR = ResMessage(
    "TOO LONG",
    "Слишком длинный!"
)

TOO_MUCH_ERR = ResMessage(
    "TOO MUCH",
    "Слишком много!"
)

TOO_SHORT_ERR = ResMessage(
    "TOO SHORT",
    "Слишком короткий!"
)

TOO_SIMPLE_ERR = ResMessage(
    "TOO SIMPLE",
    "Слишком простой!"
)

UNKNOWN_ERR = ResMessage(
    "UNKNOWN ERROR",
    "Неизвестная ошибка!"
)

VAL_ERR = ResMessage(
    "INCORRECT VALUE",
    "Некорректное значение!"
)

VAL_MISSED_ERR = ResMessage(
    "VALUE MISSED",
    "Пропущено значение!"
)
