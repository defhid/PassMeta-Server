__all__ = ('ResultMore', 'MORE', )

from App.models.okbad.result_more_code import *

import App.translate as translate


class ResultMore:
    __slots__ = ('code', 'what', 'arg')

    def __init__(self, code: ResultMoreCode, what: str | None, arg: str | None):
        self.code = code
        self.what = what
        self.arg = arg

    def __repr__(self):
        return f"<ResultMore #{self.code}, {self.what}, '{self.arg}'>"

    def to_message(self, locale: str) -> str:
        if self.code is INFO:
            return str(self.arg)

        text = translate.get_package_text(translate.OK_BAD_MORE_TRANSLATE_PACK, self.code, locale, self.code.name)

        if self.what is not None:
            text = translate.get_package_text(translate.OK_BAD_MORE_WHAT_TRANSLATE_PACK, self.what, locale, self.what) + ": " + text

        return text.format(self.arg) if self.arg else text


class MORE:
    @staticmethod
    def info(text: str) -> ResultMore:
        return ResultMore(INFO, None, text)

    @staticmethod
    def value_few(what: str, minimum) -> ResultMore:
        return ResultMore(VALUE_FEW, what, str(minimum))

    @staticmethod
    def value_much(what: str, maximum) -> ResultMore:
        return ResultMore(VALUE_MUCH, what, str(maximum))

    @staticmethod
    def value_short(what: str, minimum) -> ResultMore:
        return ResultMore(VALUE_SHORT, what, str(minimum))

    @staticmethod
    def value_long(what: str, maximum) -> ResultMore:
        return ResultMore(VALUE_LONG, what, str(maximum))

    @staticmethod
    def value_missed(what: str) -> ResultMore:
        return ResultMore(VALUE_MISSED, what, None)

    @staticmethod
    def value_wrong(what: str) -> ResultMore:
        return ResultMore(VALUE_WRONG, what, None)

    @staticmethod
    def value_already_used(what: str) -> ResultMore:
        return ResultMore(VALUE_ALREADY_USED, what, None)

    @staticmethod
    def format_wrong(what: str, accept_format: str) -> ResultMore:
        return ResultMore(FORMAT_WRONG, what, accept_format)

    @staticmethod
    def frozen(what: str) -> ResultMore:
        return ResultMore(FROZEN, what, None)

    @staticmethod
    def not_found(what: str) -> ResultMore:
        return ResultMore(NOT_FOUND, what, None)
