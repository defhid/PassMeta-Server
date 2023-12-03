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


OK = ResultCode(0, 200, "OK")
ACCESS_ERR = ResultCode(1, 403, "ACCESS ERROR")
AUTH_ERR = ResultCode(2, 401, "AUTH ERROR")
VALIDATION_ERR = ResultCode(3, 400, "INVALID DATA")
SERVER_ERR = ResultCode(4, 500, "SERVER ERROR")
