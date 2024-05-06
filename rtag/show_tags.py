from colorama import Fore
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.metadata.metadata import Metadata
from rtag.fs import walk_dir
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
        for p in walk_dir(path, ignore_dirs=MUSIC_IGNORE_DIRS, include_exts=MUSIC_INCLUDE_EXTS):
            cprint(Fore.LIGHTCYAN_EX, "/".join(p.relative_to(path).parts))
            show(path=p)
    else:
        banner(f"Tags for {path}", upper=False)
        show(path=path)
