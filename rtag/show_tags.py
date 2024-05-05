from colorama import Fore
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.fs import walk_dir
from rtag.metadata.metadata import Metadata


def do_show_tags(ctx, dir):
    for p in walk_dir(dir, ignore_dirs=MUSIC_IGNORE_DIRS, include_exts=MUSIC_INCLUDE_EXTS):
        m = Metadata.load(p)
        cprint(Fore.LIGHTCYAN_EX, "/".join(p.relative_to(dir).parts))
        for tag in m.tags:
            value = m.get_tag(tag, default=None)
            if value is not None:
                cprint(
                    Fore.LIGHTYELLOW_EX,
                    "  ",
                    tag.ljust(25),
                    Fore.LIGHTWHITE_EX,
                    " : ",
                    Fore.LIGHTGREEN_EX,
                    value,
                    sep="")
