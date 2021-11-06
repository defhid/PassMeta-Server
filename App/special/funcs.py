from typing import Dict

__all__ = (
    'loc',
)


def loc(default: str, ru: str) -> Dict[str, str]:
    return {
        "default": default,
        "ru": ru,
    }
