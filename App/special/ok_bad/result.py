from App.special.ok_bad.code import ResultCode, OK
from App.special.ok_bad.more import *
from typing import Optional, Any, Union, List, Dict, Callable

__all__ = (
    'Result',
    'Ok',
    'Bad',
)


class Result(Exception):
    __slots__ = ('_what', '_code', '_more', '_sub')

    def __init__(self, what: Union[str, Any], code: ResultCode,
                 more: 'ResultMore' = None, sub: Union['Result', List['Result']] = None):
        super().__init__()

        self._what = what
        self._code = code
        self._more = more
        self._sub = []

        if sub:
            if isinstance(sub, Result):
                self._sub.append(sub)
            else:
                for s in sub:
                    self._sub.append(s)

    def __str__(self) -> str:
        return str(self.args[0])

    def __bool__(self) -> bool:
        return self.code is OK

    @property
    def success(self) -> bool:
        return self.code is OK

    @property
    def failure(self) -> bool:
        return self.code is not OK

    @property
    def code(self) -> ResultCode:
        return self._code

    @property
    def sub(self) -> List['Result']:
        return self.args[0].get('sub')

    @property
    def what(self) -> Optional[str]:
        return self.args[0].get('what')

    @property
    def more(self) -> Optional['ResultMore']:
        return self.args[0].get('more')

    def as_dict(self, message_provider: Callable[[ResultCode], str]) -> Dict[str, object]:
        d = {
            'code': self._code.code,
            'message': message_provider(self._code)
        }

        if self._what:
            d['what'] = self._what
        if self._more:
            d['more'] = self._more
        if self._sub:
            d['sub'] = [s.as_dict(message_provider) for s in self._sub]

        return d

    def raise_if_failure(self):
        if self.failure:
            raise self


class Bad(Result):
    __slots__ = ()

    def __init__(self, what: Any, code: ResultCode,
                 more: 'ResMore' = None, sub: Union['Result', dict, List['Result'], List[dict]] = None):
        super().__init__(what, code, more, sub)


class Ok(Result):
    __slots__ = ()

    def __init__(self, what: Any = None, code: ResultCode = OK,
                 more: 'ResMore' = None, sub: Union['Result', dict, List['Result'], List[dict]] = None):
        super().__init__(what, code, more, sub)
