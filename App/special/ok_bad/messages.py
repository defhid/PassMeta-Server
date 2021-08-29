class ResMessage(str):
    __slots__ = ('response_status_code', )
    response_status_code: int

    def __init__(self, _, response_status_code=200):
        s = super()
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


ACCESS_ERR = ResMessage(
    "ACCESS ERROR",
    403
)

ALREADY_USED_ERR = ResMessage(
    "ALREADY USED"
)

AUTH_ERR = ResMessage(
    "AUTH ERROR",
    401
)

BAD_REQUEST_ERR = ResMessage(
    "BAD REQUEST",
    400
)

DATA_ERR = ResMessage(
    "INVALID DATA"
)

FORMAT_ERR = ResMessage(
    "INCORRECT FORMAT"
)

NOT_AVAILABLE = ResMessage(
    "NOT AVAILABLE"
)

NOT_EXIST_ERR = ResMessage(
    "NOT EXIST"
)

NOT_IMPLEMENTED_ERR = ResMessage(
    "NOT IMPLEMENTED"
)

OK = ResMessage(
    "OK"
)

PROHIBITED_ERR = ResMessage(
    "PROHIBITED"
)

SERVER_ERR = ResMessage(
    "SERVER ERROR",
    500
)

SIZE_ERR = ResMessage(
    "SIZE ERROR"
)

TOO_FEW_ERR = ResMessage(
    "TOO FEW"
)

TOO_LONG_ERR = ResMessage(
    "TOO LONG"
)

TOO_MUCH_ERR = ResMessage(
    "TOO MUCH"
)

TOO_SHORT_ERR = ResMessage(
    "TOO SHORT"
)

TOO_SIMPLE_ERR = ResMessage(
    "TOO SIMPLE"
)

UNKNOWN_ERR = ResMessage(
    "UNKNOWN ERROR"
)

VAL_ERR = ResMessage(
    "INCORRECT VALUE"
)

VAL_MISSED_ERR = ResMessage(
    "VALUE MISSED"
)

WRONG_VAL_ERR = ResMessage(
    "WRONG VALUE"
)
