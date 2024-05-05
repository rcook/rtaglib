from contextlib import contextmanager
from functools import cache, cached_property, partialmethod
from rtag.config import Config
from rtag.error import UserCancelledError
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
        db_path = self._args.config_dir / "metadata.db"
        if init and db_path.is_file():
            db_path.unlink()
        return MetadataDB(db_path=db_path)

    @cached_property
    def config(self):
        config_path = self._args.config_dir / "config.yaml"
        return Config.load(config_path)

    @contextmanager
    def timing(self, operation):
        def report_end(log_level, begin_time, how_ended):
            end_time = perf_counter()
            getattr(self, f"log_{log_level}")(
                f"{op} {how_ended} after "
                f"{end_time - begin_time:.02f} s")

        op = "/".join(operation) if isinstance(operation, list) else operation
        self.log_info(f"{op} started")
        begin_time = perf_counter()

        try:
            yield
        except UserCancelledError:
            report_end(
                log_level="info",
                begin_time=begin_time,
                how_ended="cancelled")
            raise
        except SystemExit:
            report_end(
                log_level="info",
                begin_time=begin_time,
                how_ended="exited")
            raise
        except:
            report_end(
                log_level="error",
                begin_time=begin_time,
                how_ended="failed")
            raise

        report_end(
            log_level="info",
            begin_time=begin_time,
            how_ended="completed")

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
