from dataclasses import dataclass
from tagtagtag.collections import DictPlus
from tagtagtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from tagtagtag.fs import walk_dir
import mutagen


@dataclass
class ExtInfo:
    count: int
    tag_infos: DictPlus


@dataclass
class TagInfo:
    count: int


def do_scan(ctx, dir):
    ext_infos = DictPlus()
    for p in walk_dir(dir=dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
        ext = p.suffix.lower()
        ext_info = ext_infos.get_or_add(
            ext,
            lambda: ExtInfo(count=0, tag_infos=DictPlus()))

        ext_info.count += 1

        m = mutagen.File(p)
        if m.tags is not None:
            for k in m.tags.keys():
                tag_info = ext_info.tag_infos.get_or_add(
                    k,
                    lambda: TagInfo(count=0))
                tag_info.count += 1

    for ext in sorted(ext_infos.keys()):
        ext_info = ext_infos[ext]
        print(f"{ext} ({ext_info.count})")
        for k in sorted(ext_info.tag_infos.keys()):
            tag_info = ext_info.tag_infos[k]
            print(f"  {k}: {tag_info.count}")
