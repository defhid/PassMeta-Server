from App.special.classes import Locale, Enum

__all__ = (
    'Locales',
)


class Locales(Enum[Locale, str]):
    RU = Locale('ru')
    DEFAULT = Locale('default')

    @classmethod
    def init(cls):
        cls._init(Locale, lambda i: i.code)


Locales.init()
