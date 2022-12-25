__all__ = (
    'loc',
    'get_package_text',
    'reverse_translate_package',
)

from App.translate.locales import Locale
from typing import Any, Callable, TypeVar


TSource = TypeVar('TSource')
TEntity = TypeVar('TEntity')


def loc(default: str, ru: str) -> dict[str, str]:
    return {
        Locale.DEFAULT: default,
        Locale.RU: ru,
    }


def get_package_text(package: dict[Any, dict[str, str]],
                     section: Any,
                     locale: str,
                     default: Any) -> str:
    pack = package.get(section)
    if pack is None:
        return str(default)

    message = pack.get(locale)
    if message is None:
        message = pack.get(Locale.DEFAULT)
        if message is None:
            return str(default)

    return message


def reverse_translate_package(package: dict[TSource, dict[str, str]],
                              item_creator: Callable[[TSource, str], TEntity]) -> dict[str, list[TEntity]]:
    d = {
        Locale.DEFAULT: [],
        Locale.RU: [],
    }
    for key in package:
        pack = package[key]
        for locale in pack:
            d[locale].append(item_creator(key, pack[locale]))
    return d
