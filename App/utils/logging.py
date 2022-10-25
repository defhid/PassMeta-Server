from App.settings import DEBUG
from typing import Callable
import logging

__all__ = (
    'LoggerFactory',
    'init_logging',
)


class Logger:
    __slots__ = ('_logger_prefix', )

    _log_info: Callable
    _log_error: Callable
    _log_critical: Callable

    def __init__(self, logger_prefix: str):
        self._logger_prefix = logger_prefix + " "

    def info(self, message: str, *format_args):
        self._log_info(self._logger_prefix + message.format(format_args))

    def error(self, message: str, *format_args, ex: BaseException = None, include_stack: bool = True):
        self._log_error(self._logger_prefix + message.format(format_args), exc_info=ex, stack_info=include_stack)

    def critical(self, message: str, *format_args, ex: BaseException = None, include_stack: bool = True):
        self._log_critical(self._logger_prefix + message.format(format_args), exc_info=ex, stack_info=include_stack)


class LoggerFactory:
    _registered = dict()

    @classmethod
    def get_named(cls, logger_name: str) -> 'Logger':
        if logger_name not in cls._registered:
            cls._registered[logger_name] = Logger(f"[{logger_name}]")
        return cls._registered[logger_name]


def init_logging(logger_name: str):
    logger = logging.getLogger(logger_name)
    Logger._log_info = logger.error if DEBUG else logger.info
    Logger._log_error = logger.error
    Logger._log_critical = logger.critical
