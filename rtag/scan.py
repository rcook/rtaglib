from colorama import Fore
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.fs import walk_dir
from rtag.new_metadata import Metadata


def do_scan(ctx, dir):
    for p in walk_dir(dir, ignore_dirs=MUSIC_IGNORE_DIRS, include_exts=MUSIC_INCLUDE_EXTS):
        m = Metadata.load(p)
        if m.musicbrainz_track_id is not None or m.rcook_track_id is not None:
            cprint(Fore.LIGHTCYAN_EX, f"{p.name}")
            for k in m.tags:
                value = m.get_tag(k, None)
                if value is not None:
                    cprint(
                        Fore.LIGHTYELLOW_EX,
                        "  ",
                        k.ljust(25),
                        Fore.LIGHTWHITE_EX,
                        " : ",
                        Fore.LIGHTGREEN_EX,
                        value,
                        sep="")