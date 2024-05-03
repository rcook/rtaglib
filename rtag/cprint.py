from colorama import Style
from io import StringIO


def cprint(fore, *args, end=None, file=None, **kwargs):
    with StringIO() as stream:
        print(*args, **kwargs, end="", file=stream)
        s = stream.getvalue()
    print(fore, s, Style.RESET_ALL, end=end, sep="", file=file)
