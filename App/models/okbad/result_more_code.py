class ResultMoreCode:
    __slots__ = ('name', )
    name: str

    def __init__(self, name: str):
        s = super()
        s.__setattr__('name', name)

    def __repr__(self):
        return self.name

    def __setattr__(self, key, value):
        raise TypeError(f"{type(self).__name__} object is immutable!")

    def __delattr__(self, item):
        raise TypeError(f"{type(self).__name__} object is immutable!")


INFO = ResultMoreCode("INFO")
VALUE_FEW = ResultMoreCode("TOO FEW")
VALUE_MUCH = ResultMoreCode("TOO MUCH")
VALUE_SHORT = ResultMoreCode("TOO SHORT")
VALUE_LONG = ResultMoreCode("TOO LONG")
VALUE_MISSED = ResultMoreCode("MISSED")
VALUE_WRONG = ResultMoreCode("WRONG VALUE")
VALUE_ALREADY_USED = ResultMoreCode("ALREADY USED")
FORMAT_WRONG = ResultMoreCode("WRONG FORMAT")
FROZEN = ResultMoreCode("FROZEN")
NOT_FOUND = ResultMoreCode("NOT EXIST")
