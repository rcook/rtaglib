from colorama import Fore
from dataclasses import dataclass
from rtag.collections import DictPlus
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.metadata.new_metadata import Metadata
from rtag.fs import walk_dir


@dataclass(frozen=False)
class TagInfo:
    tag: str
    count: int

    @classmethod
    def default(cls, tag):
        return cls(tag=tag, count=0)


@dataclass(frozen=False)
class ExtInfo:
    ext: str
    count: int
    tags: DictPlus[str, TagInfo]

    @classmethod
    def default(cls, ext):
        return cls(ext=ext, count=0, tags=DictPlus())


def show_tag_stats(ctx, dir):
    exts = DictPlus()
    for p in walk_dir(dir, ignore_dirs=MUSIC_IGNORE_DIRS, include_exts=MUSIC_INCLUDE_EXTS):
        ext = p.suffix.lower()
        m = Metadata.load(p)
        print("/".join(p.relative_to(dir).parts))
        ext_info = exts.get_or_add(ext, lambda k: ExtInfo.default(ext=k))
        ext_info.count += 1
        for tag in m.raw_tags:
            tag_info = ext_info.tags.get_or_add(
                tag,
                lambda k: TagInfo.default(tag=k))
            tag_info.count += 1

    for ext in sorted(exts.keys()):
        ext_info = exts[ext]
        cprint(Fore.LIGHTCYAN_EX, f"{ext}: {ext_info.count}")
        for tag, tag_info in sorted(
                ext_info.tags.items(),
                key=lambda t: (-t[1].count, t[1].tag)):
            cprint(
                Fore.LIGHTYELLOW_EX,
                "  ",
                tag.ljust(40),
                " ",
                Fore.LIGHTGREEN_EX,
                f"{tag_info.count / ext_info.count:.00%}",
                sep="")

    total = sum(map(lambda x: x.count, exts.values()))
    print(f"Total: {total}")


def do_list_dir(ctx, dir, mode):
    match mode:
        case "show-tag-stats": show_tag_stats(ctx=ctx, dir=dir)
        case _: raise NotImplementedError(f"Unsupported mode {mode}")
