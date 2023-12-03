__all__ = ('Result', 'Ok', 'Bad', )

from App.models.okbad.result_code import ResultCode, OK
from App.models.okbad.result_more import *


class Result(Exception):
    __slots__ = ('code', 'more')

    code: ResultCode
    more: list[ResultMore] | None

    def __init__(self,  code: ResultCode, more: ResultMore | list[ResultMore] = None):
        super().__init__()
        self.code = code
        self.more = more if type(more) is list else \
            [more] if more is not None else \
            None

    def __repr__(self) -> str:
        return f"<Result #{self.code.code} {self.code.name}>"

    def __bool__(self) -> bool:
        return self.code is OK

    def raise_if_failure(self):
        if self.code is not OK:
            raise self


class Bad(Result):
    __slots__ = ()

    def __init__(self, code: ResultCode, more: ResultMore | list[ResultMore] = None):
        super().__init__(code, more)


class Ok(Result):
    __slots__ = ()

    def __init__(self):
        super().__init__(OK)
