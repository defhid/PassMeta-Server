from App.special.results._messages import ResMessage, OK
from App.special.results._more import *
from starlette.responses import JSONResponse
from typing import Optional, Any, Union, List, Dict

__all__ = (
    'Result',
    'Ok',
    'Bad',
)


class Result(Exception):
    __slots__ = ()

    def __init__(self, what: Union[str, Any], message: ResMessage,
                 more: 'ResMore' = None, sub: Union['Result', dict, List['Result'], List[dict]] = None):
        super().__init__(dict())
        self(
            what=what,
            message=message,
            more=more,
            sub=sub
        )

    def __str__(self) -> str:
        return str(self.args[0])

    def __call__(self, **kwargs) -> 'Result':
        """ Set attributes """
        for field in kwargs:
            val = kwargs[field]
            if val is not None:
                setattr(self, field, val)
        return self

    @property
    def what(self) -> Optional[str]:
        return self.args[0].get('what')

    @what.setter
    def what(self, value: Optional[Any]):
        if value is None:
            self.args[0].pop('what', None)
        else:
            self.args[0]['what'] = value

    @property
    def message(self) -> Union[ResMessage, str]:
        return self.args[0].get('message')

    @message.setter
    def message(self, value: Union[ResMessage, str]):
        """ Raises ValueError if value is None """
        if value is None:
            raise ValueError("Message cannot be None!")
        self.args[0]['message'] = value

    @property
    def more(self) -> Optional['ResMore']:
        return self.args[0].get('more')

    @more.setter
    def more(self, value: Optional['ResMore']):
        if value is None:
            self.args[0].pop('more', None)
        else:
            self.args[0]['more'] = value

    @property
    def sub(self) -> Optional[List[dict]]:
        return self.args[0].get('sub')

    @sub.setter
    def sub(self, value: Optional[List[Union['Result', dict]]]):
        if value is None:
            self.args[0].pop('sub', None)
        else:
            for i in range(len(value)):
                if isinstance(value[i], Result):
                    value[i] = value[i].as_dict()
            self.args[0]['sub'] = value

    def as_dict(self) -> Dict[str, object]:
        return self.args[0]

    def as_response(self, data: Any = None) -> JSONResponse:
        if data is not None:
            self.args[0]['data'] = data
        return JSONResponse(self.args[0], status_code=self.message.response_status_code)


class Bad(Result):
    __slots__ = ()

    def __init__(self, what: Any, message: ResMessage,
                 more: 'ResMore' = None, sub: Union['Result', dict, List['Result'], List[dict]] = None):
        super().__init__(what, message, more, sub)


class Ok(Result):
    __slots__ = ()

    def __init__(self, what: Any = None, message: ResMessage = OK,
                 more: 'ResMore' = None, sub: Union['Result', dict, List['Result'], List[dict]] = None):
        super().__init__(what, message, more, sub)
