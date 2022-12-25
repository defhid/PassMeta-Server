__all__ = ('Result', 'Ok', 'Bad', )

from App.models.okbad.result_code import ResultCode, OK
from App.models.okbad.more import *
from typing import Self


class Result(Exception):
    __slots__ = ('what', 'code', 'more', 'sub')

    def __init__(self,
                 what: str | None,
                 code: ResultCode,
                 more: ResultMore = None,
                 sub: Self | list[Self] = None):
        super().__init__()

        self.what = what
        self.code = code
        self.more = more
        self.sub = []

        if sub:
            if isinstance(sub, Result):
                self.sub.append(sub)
            else:
                for s in sub:
                    self.sub.append(s)

    def __repr__(self) -> str:
        return f"<Result #{self.code.code} {self.code.name}>"

    def __bool__(self) -> bool:
        return self.code is OK

    @property
    def success(self) -> bool:
        return self.code is OK

    @property
    def failure(self) -> bool:
        return self.code is not OK

    def raise_if_failure(self):
        if self.failure:
            raise self


class Bad(Result):
    __slots__ = ()

    def __init__(self,
                 what: str | None,
                 code: ResultCode,
                 more: ResultMore = None,
                 sub: Self | list[Self] = None):
        super().__init__(what, code, more, sub)


class Ok(Result):
    __slots__ = ()

    def __init__(self):
        super().__init__(None, OK)
