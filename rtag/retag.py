from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.fs import walk_dir


def do_retag(ctx, dir):
    print(dir)
    with ctx.open_db():
        for p in walk_dir(dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            print(p)
