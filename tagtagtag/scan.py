from dataclasses import dataclass
from tagtagtag.fs import walk_dir
import mutagen


_IGNORE_DIRS = {
    ".git",
    ".vscode",
    "__pycache__"
}

_INCLUDE_EXTS = {
    ".flac",
    ".m4a",
    ".mp3",
    ".wma"
}


@dataclass
class ExtInfo:
    count: int
    tag_infos: dict


@dataclass
class TagInfo:
    count: int


def do_scan(ctx, dir):
    ext_infos = {}
    for p in walk_dir(dir=dir, include_exts=_INCLUDE_EXTS, ignore_dirs=_IGNORE_DIRS):
        ext = p.suffix.lower()
        ext_info = ext_infos.get(ext)
        if ext_info is None:
            ext_info = ExtInfo(count=0, tag_infos={})
            ext_infos[ext] = ext_info

        ext_info.count += 1

        m = mutagen.File(p)
        if m.tags is not None:
            for k in m.tags.keys():
                tag_info = ext_info.tag_infos.get(k)
                if tag_info is None:
                    tag_info = TagInfo(count=0)
                    ext_info.tag_infos[k] = tag_info
                tag_info.count += 1

    for ext in sorted(ext_infos.keys()):
        ext_info = ext_infos[ext]
        print(f"{ext} ({ext_info.count})")
        for k in sorted(ext_info.tag_infos.keys()):
            tag_info = ext_info.tag_infos[k]
            print(f"  {k}: {tag_info.count}")
