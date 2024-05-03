from functools import cache, cached_property, partialmethod
from rtag.config import Config
import inspect
import logging


class ContextMeta(type):
    def __new__(cls, name, bases, dct):
        t = super().__new__(cls, name, bases, dct)

        for log_level in logging.getLevelNamesMapping().keys() - {"NOTSET", "WARN"}:
            def log(self, log_level, *args, **kwargs):
                frame = inspect.stack()[1]
                module = inspect.getmodule(frame[0])
                logger = self._logger(module.__name__)
                method = getattr(logger, log_level)
                return method(*args, **kwargs)

            log_level = log_level.lower()
            setattr(t, f"log_{log_level}", partialmethod(log, log_level))

        return t


class Context(metaclass=ContextMeta):
    def __init__(self, args, log_level=logging.DEBUG):
        self._args = args
        self._log_level = log_level

    @cached_property
    def config(self):
        return Config.load(self._args.config_path)

    @cache
    def _logger(self, name):
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        handler = logging.StreamHandler()
        handler.setLevel(self._log_level)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(self._log_level)
        logger.addHandler(handler)
        return logger
