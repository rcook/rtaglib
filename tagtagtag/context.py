from functools import cache
import inspect
import logging


class Context:
    _LOG_METHOD_PREFIX = "log_"
    _LOG_LEVEL_NAMES = set(
        map(
            lambda m: m.lower(),
            logging.getLevelNamesMapping().keys() - {"NOTSET", "WARN"}))

    def __init__(self, log_level=logging.DEBUG):
        self._log_level = log_level

    def __getattr__(self, name):
        if name.startswith(self.__class__._LOG_METHOD_PREFIX):
            log_level = name[len(self.__class__._LOG_METHOD_PREFIX):]
            if log_level in self._LOG_LEVEL_NAMES:
                def log(*args, **kwargs):
                    frame = inspect.stack()[1]
                    module = inspect.getmodule(frame[0])
                    logger = self._logger(module.__name__)
                    method = getattr(logger, log_level)
                    return method(*args, **kwargs)
                return log
        raise AttributeError(
            "Undefined attribute "
            f"{self.__class__.__name__}.{name}")

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
