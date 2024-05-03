from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timing(ctx, operation):
    ctx.log_info(f"{operation} started")
    begin = perf_counter()
    yield
    end = perf_counter()
    ctx.log_info(f"{operation} completed in {end - begin:.02f} s")
