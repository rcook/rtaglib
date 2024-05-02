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


class DictPlus(dict):
    _MISSING = object()

    def get_or_add(self, key, func):
        value = self.get(key, self.__class__._MISSING)
        if value is self.__class__._MISSING:
            value = func()
            self[key] = value
        return value


@dataclass
class ExtInfo:
    count: int
    tag_infos: DictPlus


@dataclass
class TagInfo:
    count: int


def do_scan(ctx, dir):
    ext_infos = DictPlus()
    for p in walk_dir(dir=dir, include_exts=_INCLUDE_EXTS, ignore_dirs=_IGNORE_DIRS):
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
