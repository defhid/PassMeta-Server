from pydantic import BaseModel

__all__ = ('BaseDto', )

def to_camel_case(string: str) -> str:
    string_split = string.split("_")
    return string_split[0] + "".join(word.capitalize() for word in string_split[1:])


class BaseDto(BaseModel):
    class Config:
        alias_generator = to_camel_case