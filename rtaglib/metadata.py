from abc import ABCMeta, abstractmethod
from dataclasses import MISSING
from functools import cached_property, partial
from pathlib import Path
from rtaglib.pos import Pos
from typing import Any, Callable, Sequence, Tuple
from uuid import UUID


ARTIST_TITLE_ATTR = "artist_title"
ALBUM_TITLE_ATTR = "album_title"
TRACK_TITLE_ATTR = "track_title"
TRACK_DISC_ATTR = "track_disc"
TRACK_NUMBER_ATTR = "track_number"
MUSICBRAINZ_ARTIST_ID_ATTR = "musicbrainz_artist_id"
MUSICBRAINZ_ALBUM_ID_ATTR = "musicbrainz_album_id"
MUSICBRAINZ_TRACK_ID_ATTR = "musicbrainz_track_id"
RCOOK_ARTIST_ID_ATTR = "rcook_artist_id"
RCOOK_ALBUM_ID_ATTR = "rcook_album_id"
RCOOK_TRACK_ID_ATTR = "rcook_track_id"


class MetadataMeta(ABCMeta):
    _TAGS: Sequence[Tuple[str, type, Callable]] = [
        (ARTIST_TITLE_ATTR, str, str),
        (ALBUM_TITLE_ATTR, str, str),
        (TRACK_TITLE_ATTR, str, str),
        (TRACK_DISC_ATTR, Pos, Pos.check),
        (TRACK_NUMBER_ATTR, Pos, Pos.check),
        (MUSICBRAINZ_ARTIST_ID_ATTR, UUID, UUID),
        (MUSICBRAINZ_ALBUM_ID_ATTR, UUID, UUID),
        (MUSICBRAINZ_TRACK_ID_ATTR, UUID, UUID),
        (RCOOK_ARTIST_ID_ATTR, UUID, UUID),
        (RCOOK_ALBUM_ID_ATTR, UUID, UUID),
        (RCOOK_TRACK_ID_ATTR, UUID, UUID)
    ]
    _TO_TAG_INFOS: dict[str, Tuple[type, Callable]] = {
        tag: (tag_type, tag_ctor)
        for tag, tag_type, tag_ctor in _TAGS
    }

    def __new__(cls, name, bases, dct):
        def fget(tag, self):
            return self.get_tag(tag, default=None)

        def fset(tag, self, value):
            return self.set_tag(tag, value)

        def fdel(tag, self):
            return self.del_tag(tag)

        t = super().__new__(cls, name, bases, dct)
        for tag, _, _ in cls._TAGS:
            setattr(
                t,
                tag,
                property(partial(fget, tag), partial(fset, tag), partial(fdel, tag)))
        return t


class Metadata(metaclass=MetadataMeta):
    @staticmethod
    def load(path: Path) -> "Metadata":
        from rtaglib.flac_metadata import FLACMetadata
        from rtaglib.mp3_metadata import MP3Metadata
        from rtaglib.mp4_metadata import MP4Metadata
        from rtaglib.wma_metadata import WMAMetadata
        import mutagen
        import mutagen.asf
        import mutagen.flac
        import mutagen.mp3
        import mutagen.mp4

        m = mutagen.File(path)
        match m:
            case mutagen.flac.FLAC(): return FLACMetadata(m=m)
            case mutagen.mp3.MP3(): return MP3Metadata(m=m)
            case mutagen.mp4.MP4(): return MP4Metadata(m=m)
            case mutagen.asf.ASF(): return WMAMetadata(m=m)
            case _: raise NotImplementedError(f"Unsupported metadata type {type(m)} in file {path}")

    def __init__(self, m: Any) -> None:
        self._m = m

    def __str__(self) -> str:
        tags = "; ".join(
            f"{k}={v}"
            for k, v in
            [
                (tag, self.get_tag(tag, default=None))
                for tag in sorted(self.tags)
            ]
            if v is not None)
        return f"<[{self.__class__.__name__}] {tags}>"

    @cached_property
    def tags(self) -> Sequence[str]:
        return [tag for tag, _, _ in self.__class__._TAGS]

    @property
    def raw_tags(self) -> Sequence[str]:
        return self._m.tags.keys()

    def save(self) -> None:
        self._m.save()

    def pprint(self) -> str:
        return self._m.tags.pprint()

    def get_tag(self, tag: str, default: Any = MISSING) -> Any:
        getter = getattr(self, f"_get_{tag}", None)
        if getter is None:
            value = self._get_tag(tag, default=default)
        else:
            value = getter(default=default)

        tag_ctor = self.__class__._TO_TAG_INFOS[tag][1]
        return value if value is None else tag_ctor(value)

    def set_tag(self, tag: str, value: Any) -> None:
        tag_type = self.__class__._TO_TAG_INFOS[tag][0]
        if not isinstance(value, tag_type):
            raise ValueError(
                f"Value {value} is not of required type "
                f"{tag_type.__name__}")

        setter = getattr(self, f"_set_{tag}", None)
        if setter is None:
            self._set_tag(tag, value)
        else:
            setter(value)

    def del_tag(self, tag: str) -> None:
        deleter = getattr(self, f"_del_{tag}", None)
        if deleter is None:
            self._del_tag(tag)
        else:
            deleter()

    @abstractmethod
    def _get_tag(self, name: str, default: Any = MISSING) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def _set_tag(self, name: str, value: Any) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _del_tag(self, name: str) -> None:
        raise NotImplementedError()
