from typing import Any, Union, Dict

__all__ = (
    'ResMore',
    'MORE',
)


class ResMore(dict):

    def text(self, value: str) -> 'ResMore':
        self['text'] = value
        return self

    def info(self, *values: Dict[str, Any]) -> 'ResMore':
        if 'info' in self:
            self['info'].extend(values)
        else:
            self['info'] = list(values)
        return self

    def allowed(self, *values: Any) -> 'ResMore':
        if 'allowed' in self:
            self['allowed'].extend(values)
        else:
            self['allowed'] = list(values)
        return self

    def disallowed(self, *values: Any) -> 'ResMore':
        if 'disallowed' in self:
            self['disallowed'].extend(values)
        else:
            self['disallowed'] = list(values)
        return self

    def required(self, *values: Any) -> 'ResMore':
        if 'required' in self:
            self['required'].extend(values)
        else:
            self['required'] = list(values)
        return self

    def related(self, *values: Any) -> 'ResMore':
        if 'related' in self:
            self['related'].extend(values)
        else:
            self['related'] = list(values)
        return self

    def min_allowed(self, value: Union[int, float]) -> 'ResMore':
        self['min_allowed'] = value
        return self

    def max_allowed(self, value: Union[int, float]) -> 'ResMore':
        self['max_allowed'] = value
        return self


class MORE:

    @staticmethod
    def text(val: str) -> ResMore:
        return ResMore(text=val)

    @staticmethod
    def info(*values: Dict[str, Any]):
        return ResMore(info=list(values))

    @staticmethod
    def allowed(*values: Any) -> ResMore:
        return ResMore(allowed=list(values))

    @staticmethod
    def disallowed(*values: Any) -> ResMore:
        return ResMore(disallowed=list(values))

    @staticmethod
    def required(*values: Any) -> ResMore:
        return ResMore(required=list(values))

    @staticmethod
    def related(*values: Any) -> ResMore:
        return ResMore(related=list(values))

    @staticmethod
    def min_allowed(val: Union[int, float]) -> ResMore:
        return ResMore(min_allowed=val)

    @staticmethod
    def max_allowed(val: Union[int, float]) -> ResMore:
        return ResMore(max_allowed=val)
