from contextlib import contextmanager
from functools import cache, cached_property, partialmethod
from rtag.config import Config
from rtag.metadata_db import MetadataDB
from time import perf_counter
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

    def open_db(self, init=False):
        db_path = self._args.data_dir / "metadata.db"
        if init and db_path.is_file():
            db_path.unlink()
        return MetadataDB(db_path=db_path)

    @cached_property
    def config(self):
        return Config.load(self._args.config_path)

    @contextmanager
    def timing(self, operation):
        self.log_info(f"{operation} started")
        begin_time = perf_counter()

        try:
            yield
        except:
            end_time = perf_counter()
            self.log_error(
                f"{operation} failed after "
                f"{end_time - begin_time:.02f} s")
            raise

        end_time = perf_counter()
        self.log_info(
            f"{operation} completed in "
            f"{end_time - begin_time:.02f} s")

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
