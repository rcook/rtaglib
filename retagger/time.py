from colorama import Fore
from contextlib import contextmanager
from retagger.cprint import cprint
from time import perf_counter


@contextmanager
def timing(operation):
    cprint(Fore.LIGHTCYAN_EX, f"===== BEGIN: {operation} =====")
    begin = perf_counter()
    yield
    end = perf_counter()
    cprint(Fore.LIGHTCYAN_EX, f"===== END: {
           operation} completed in {end - begin:.02f} seconds =====")
    cprint(Fore.LIGHTCYAN_EX, f"")
