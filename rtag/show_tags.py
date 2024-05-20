from colorama import Fore
from rpycli.fs import iter_files
from rpycli.prelude import *
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.metadata.metadata import Metadata
from rtag.ui import banner


def do_show_tags(ctx, path):
    def show(path):
        m = Metadata.load(path)
        cprint(Fore.LIGHTMAGENTA_EX, "  ", "Normalized tags", sep="")
        for tag in sorted(m.tags):
            value = m.get_tag(tag, default=None)
            if value is not None:
                cprint(
                    Fore.LIGHTYELLOW_EX,
                    "    ",
                    tag.ljust(25),
                    Fore.LIGHTWHITE_EX,
                    " : ",
                    Fore.LIGHTGREEN_EX,
                    value,
                    sep="")

        cprint(Fore.LIGHTMAGENTA_EX, "  Raw tags")
        for line in sorted(m.pprint().splitlines()):
            cprint(Fore.LIGHTYELLOW_EX, "    ", line, sep="")

    if path.is_dir():
        banner(f"Tags for files in {path}", upper=False)
        for p in iter_files(path, include_suffixes=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            cprint(Fore.LIGHTCYAN_EX, "/".join(p.relative_to(path).parts))
            show(path=p)
    else:
        banner(f"Tags for {path}", upper=False)
        show(path=path)
