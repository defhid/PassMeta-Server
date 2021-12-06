from App.special.consts import Locales
from typing import Dict

__all__ = (
    'loc',
)


def loc(default: str, ru: str) -> Dict[str, str]:
    return {
        Locales.DEFAULT.code: default,
        Locales.RU.code: ru,
    }
