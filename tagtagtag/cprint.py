from colorama import Style
from io import StringIO


def cprint(fore, *args, file=None, **kwargs):
    with StringIO() as stream:
        print(*args, **kwargs, file=stream)
        s = stream.getvalue()
    print(fore, s, Style.RESET_ALL, end="", sep="", file=file)
