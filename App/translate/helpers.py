from App.translate.locales import Locale
from typing import Dict, Any, Callable, TypeVar, List

__all__ = (
    'loc',
    'get_package_text',
    'reverse_translate_package',
)

TSource = TypeVar('TSource')
TEntity = TypeVar('TEntity')


def loc(default: str, ru: str) -> Dict[str, str]:
    return {
        Locale.DEFAULT: default,
        Locale.RU: ru,
    }


def get_package_text(package: Dict[Any, Dict[str, str]],
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


def reverse_translate_package(package: Dict[TSource, Dict[str, str]],
                              item_creator: Callable[[TSource, str], TEntity]) -> Dict[str, List[TEntity]]:
    d = {
        Locale.DEFAULT: [],
        Locale.RU: [],
    }
    for key in package:
        pack = package[key]
        for locale in pack:
            d[locale].append(item_creator(key, pack[locale]))
    return d
