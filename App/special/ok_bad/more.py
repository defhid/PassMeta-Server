from typing import Any, Union, Dict

__all__ = (
    'ResultMore',
    'MORE',
)


class ResultMore(dict):
    __slots__ = ()

    def text(self, value: str) -> 'ResultMore':
        self['text'] = value
        return self

    def info(self, *values: Dict[str, Any]) -> 'ResultMore':
        if 'info' in self:
            self['info'].extend(values)
        else:
            self['info'] = list(values)
        return self

    def allowed(self, *values: Any) -> 'ResultMore':
        if 'allowed' in self:
            self['allowed'].extend(values)
        else:
            self['allowed'] = list(values)
        return self

    def disallowed(self, *values: Any) -> 'ResultMore':
        if 'disallowed' in self:
            self['disallowed'].extend(values)
        else:
            self['disallowed'] = list(values)
        return self

    def required(self, *values: Any) -> 'ResultMore':
        if 'required' in self:
            self['required'].extend(values)
        else:
            self['required'] = list(values)
        return self

    def min_allowed(self, value: Union[int, float]) -> 'ResultMore':
        self['min_allowed'] = value
        return self

    def max_allowed(self, value: Union[int, float]) -> 'ResultMore':
        self['max_allowed'] = value
        return self


class MORE:

    @staticmethod
    def text(val: str) -> ResultMore:
        return ResultMore(text=val)

    @staticmethod
    def info(*values: Dict[str, Any]):
        return ResultMore(info=list(values))

    @staticmethod
    def allowed(*values: Any) -> ResultMore:
        return ResultMore(allowed=list(values))

    @staticmethod
    def disallowed(*values: Any) -> ResultMore:
        return ResultMore(disallowed=list(values))

    @staticmethod
    def required(*values: Any) -> ResultMore:
        return ResultMore(required=list(values))

    @staticmethod
    def min_allowed(val: Union[int, float, str]) -> ResultMore:
        return ResultMore(min_allowed=val)

    @staticmethod
    def max_allowed(val: Union[int, float, str]) -> ResultMore:
        return ResultMore(max_allowed=val)

    @staticmethod
    def exception(ex: BaseException) -> ResultMore:
        return ResultMore(text=str(ex))
