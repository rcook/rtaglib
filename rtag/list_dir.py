from colorama import Fore
from dataclasses import dataclass, replace
from rtag.collections import DictPlus
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.metadata.metadata import Metadata
from rtag.fs import walk_dir


WELL_KNOWN_RAW_TAGS = {
    ".flac": {
        "album",
        "albumartist",
        "albumartistsort",
        "artist",
        "artists",
        "artistsort",
        "discnumber",
        "disctotal",
        "musicbrainz_albumartistid",
        "musicbrainz_albumid",
        "musicbrainz_artistid",
        "musicbrainz_releasegroupid",
        "musicbrainz_releasetrackid",
        "musicbrainz_trackid",
        "rcook_album_id",
        "rcook_artist_id",
        "rcook_track_id",
        "title",
        "totaldiscs",
        "totaltracks",
        "tracknumber",
        "tracktotal"
    },
    ".m4a": {
        "\xa9alb",
        "\xa9nam",
        "aART",
        "disk",
        "trkn",
        "----:com.apple.iTunes:MusicBrainz Album Artist Id",
        "----:com.apple.iTunes:MusicBrainz Album Id",
        "----:com.apple.iTunes:MusicBrainz Album Release Country",
        "----:com.apple.iTunes:MusicBrainz Album Status",
        "----:com.apple.iTunes:MusicBrainz Album Type",
        "----:com.apple.iTunes:MusicBrainz Artist Id",
        "----:com.apple.iTunes:MusicBrainz Release Group Id",
        "----:com.apple.iTunes:MusicBrainz Release Track Id",
        "----:com.apple.iTunes:MusicBrainz Track Id",
        "----:org.rcook:AlbumId",
        "----:org.rcook:ArtistId",
        "----:org.rcook:TrackId"
    },
    ".mp3": {
        "TIT2",
        "TPOS",
        "TRCK",
        "TXXX:MusicBrainz Album Artist Id",
        "TXXX:MusicBrainz Album Id",
        "TXXX:MusicBrainz Album Release Country",
        "TXXX:MusicBrainz Album Status",
        "TXXX:MusicBrainz Album Type",
        "TXXX:MusicBrainz Artist Id",
        "TXXX:MusicBrainz Release Group Id",
        "TXXX:MusicBrainz Release Track Id",
        "TXXX:org.rcook/AlbumId",
        "TXXX:org.rcook/ArtistId",
        "TXXX:org.rcook/TrackId"
    },
    ".wma": {
        "MusicBrainz/Album Artist Id",
        "MusicBrainz/Album Id",
        "MusicBrainz/Album Release Country",
        "MusicBrainz/Album Status",
        "MusicBrainz/Album Type",
        "MusicBrainz/Artist Id",
        "MusicBrainz/Release Group Id",
        "MusicBrainz/Release Track Id",
        "MusicBrainz/Track Id",
        "org.rcook/AlbumId",
        "org.rcook/ArtistId",
        "org.rcook/TrackId",
        "Title",
        "WM/AlbumArtist",
        "WM/AlbumTitle",
        "WM/PartOfSet",
        "WM/Track",
        "WM/TrackNumber"
    }
}


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


def show_raw_tags(ctx, dir, exclude_well_known_raw_tags=True):
    exts = DictPlus()
    for p in walk_dir(dir, ignore_dirs=MUSIC_IGNORE_DIRS, include_exts=MUSIC_INCLUDE_EXTS):
        ext = p.suffix.lower()
        well_known_raw_tags = WELL_KNOWN_RAW_TAGS.get(ext, set()) \
            if exclude_well_known_raw_tags \
            else set()
        m = Metadata.load(p)
        print("/".join(p.relative_to(dir).parts))
        ext_info = exts.get_or_add(ext, lambda k: ExtInfo.default(ext=k))
        ext_info.count += 1
        # if ext == ".wma":
        #    print(m.pprint())
        #    exit(0)
        for tag in m.raw_tags:
            if tag not in well_known_raw_tags:
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


def show_tags(ctx, dir):
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
                    ": ",
                    Fore.LIGHTGREEN_EX,
                    value,
                    sep="")


def do_list_dir(ctx, dir, mode):
    match mode:
        case "show-raw-tags": show_raw_tags(ctx=ctx, dir=dir)
        case "show-tags": show_tags(ctx=ctx, dir=dir)
        case _: raise NotImplementedError(f"Unsupported mode {mode}")
