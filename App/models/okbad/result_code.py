class ResultCode:
    __slots__ = ('code', 'response_status_code', 'name')
    code: int
    response_status_code: int
    name: str

    def __init__(self, code: int, response_status_code: int, name: str):
        s = super()
        s.__setattr__('code', code)
        s.__setattr__('response_status_code', response_status_code)
        s.__setattr__('name', name)

    def __repr__(self):
        return f"<ResultCode #{self.code}, {self.response_status_code}, '{self.name}'>"

    def __setattr__(self, key, value):
        raise TypeError(f"{type(self).__name__} object is immutable!")

    def __delattr__(self, item):
        raise TypeError(f"{type(self).__name__} object is immutable!")


ACCESS_ERR = ResultCode(1, 403, "ACCESS ERROR")

ALREADY_USED_ERR = ResultCode(2, 200, "ALREADY USED")

AUTH_ERR = ResultCode(3, 401, "AUTH ERROR")

BAD_REQUEST_ERR = ResultCode(4, 400, "BAD REQUEST")

DATA_ERR = ResultCode(5, 200, "INVALID DATA")

FORMAT_ERR = ResultCode(6, 200, "INCORRECT FORMAT")

FROZEN_ERR = ResultCode(7, 200, "FROZEN")

NOT_EXIST_ERR = ResultCode(8, 200, "NOT EXIST")

NOT_IMPLEMENTED_ERR = ResultCode(9, 200, "NOT IMPLEMENTED")

OK = ResultCode(0, 200, "OK")

PROHIBITED_ERR = ResultCode(10, 200, "PROHIBITED")

SERVER_ERR = ResultCode(11, 500, "SERVER ERROR")

TOO_FEW_ERR = ResultCode(12, 200, "TOO FEW")

TOO_LONG_ERR = ResultCode(13, 200, "TOO LONG")

TOO_MUCH_ERR = ResultCode(14, 200, "TOO MUCH")

TOO_SHORT_ERR = ResultCode(15, 200, "TOO SHORT")

VAL_ERR = ResultCode(16, 200, "INCORRECT VALUE")

VAL_MISSED_ERR = ResultCode(17, 200, "VALUE MISSED")

WRONG_VAL_ERR = ResultCode(18, 200, "WRONG VALUE")
