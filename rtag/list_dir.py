from rtag.collections import DictPlus
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.fs import walk_dir


def do_list_dir(ctx, dir):
    ctx.log_info("list-dir begin")
    exts = DictPlus()
    for p in walk_dir(dir, ignore_dirs=MUSIC_IGNORE_DIRS, include_exts=MUSIC_INCLUDE_EXTS):
        print("/".join(p.relative_to(dir).parts))
        count = exts.get_or_add(p.suffix.lower(), lambda k: [0])
        count[0] += 1

    for ext in sorted(exts.keys()):
        print(f"{ext}: {exts[ext][0]}")
    ctx.log_info("list-dir end")
