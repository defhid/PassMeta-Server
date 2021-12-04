from os import sep as os_sep
import traceback
import logging

__all__ = (
    'Logger',
)

from App.settings import DEBUG


class Logger:
    __slots__ = ('location', )

    _logger: logging.Logger

    def __init__(self, location):
        self.location = os_sep.join(location.split(os_sep)[-2:])

    def _complex_message(self, text: str, ex: BaseException, params: dict, need_trace=True) -> str:
        if need_trace:
            trace = f", ln{traceback.extract_stack()[-2].lineno}"
        else:
            trace = ""
        if params:
            data = ", " + ", ".join(f"{k}={v}" for k, v in params.items())
        else:
            data = ""
        if ex is None:
            return f"{text} ~{self.location}{trace}{data}"
        return f"{text}: {ex} ~{self.location}{trace}{data}"

    def error(self, _text: str, _ex: BaseException = None, _need_trace: bool = True, **kwargs):
        self._logger.error(self._complex_message(_text, _ex, kwargs, _need_trace))

    def critical(self, _text: str, _ex: BaseException = None, _need_trace: bool = True, **kwargs):
        self._logger.critical(self._complex_message(_text, _ex, kwargs, _need_trace))

    def info(self, _text: str, **kwargs):
        if kwargs:
            self._log_info(f"{_text} ({', '.join(f'{k}={v}' for k, v in kwargs.items())})")
        else:
            self._log_info(f"{_text}")

    @classmethod
    def init(cls, logger_name: str):
        cls._logger = logging.getLogger(logger_name)
        cls._log_info = cls._logger.error if DEBUG else cls._logger.info
