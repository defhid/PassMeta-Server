import os

__all__ = ('string', 'integer', 'boolean')


""" Get string from config value
"""
def string(key: str, default="", required=False) -> str:
    val = os.getenv(key)

    if not val:
        if required:
            raise ImportError(f"Missed required setting: {key}")
        return default

    return val


""" Get integer from config value
"""
def integer(key: str, default=0, required=False) -> int:
    val = string(key, default=str(default), required=required)
    return int(val)


""" Get boolean from config value
"""
def boolean(key: str, default=False, required=False) -> bool:
    val = string(key, default=str(default), required=required)
    return val.lower() == "true"


""" Get absolute path from config value
"""
def path(key: str, default="", required=False) -> str:
    val = string(key, default=str(default), required=required)
    return os.path.abspath(val)
