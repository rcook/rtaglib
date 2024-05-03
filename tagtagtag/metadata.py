from abc import ABCMeta, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, make_dataclass
from functools import partial
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4Tags
from typing import Callable
import mutagen
import mutagen.asf
import mutagen.easyid3
import mutagen.easymp4
import mutagen.flac
import mutagen.id3
import mutagen.mp3


_MISSING = object()
_ATTRS = [
    ("artist_title", str),
    ("album_title", str),
    ("track_title", str),
    ("track_disc", str),
    ("track_number", int),
    ("musicbrainz_artist_id", str),
    ("musicbrainz_album_id", str),
    ("musicbrainz_track_id", str)
]


@dataclass(frozen=True)
class Key:
    key: str
    func: Callable


CommonKeys = make_dataclass("CommonKeys", [
    (attr[0], str | Key)
    for attr in _ATTRS
], frozen=True)


def parse_slash_number(s):
    value, _ = s.split("/", maxsplit=1)
    return value


class MetadataMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        t = super().__new__(cls, name, bases, dct)

        for attr in _ATTRS:
            def get_tag(name, required_type, self):
                key = getattr(self.__class__.COMMON_KEYS, name)
                if isinstance(key, str):
                    value = self._scalar(key)
                else:
                    value = key.func(self._scalar(key.key))
                return None if value is None else required_type(value)

            setattr(
                t,
                attr[0],
                property(partial(get_tag, attr[0], attr[1])))

        return t


class Metadata(metaclass=MetadataMeta):
    ALBUM_ID_KEY = "rcook_album_id"
    TRACK_ID_KEY = "rcook_track_id"
    _first_instance = True

    class Accessor:
        def __init__(self, metadata, key):
            self._metadata = metadata
            self._key = key

        def get(self, default=_MISSING):
            return self._metadata.get(key=self._key, default=default)

        def set(self, value):
            self._metadata.set(key=self._key, value=value)

        def pop(self, default=_MISSING):
            self._metadata.pop(key=self._key, default=default)

    @staticmethod
    def load(path):
        inner = mutagen.File(path, easy=True)
        match inner:
            case mutagen.mp3.EasyMP3(): return ID3Metadata(path=path, inner=inner)
            case mutagen.easymp4.EasyMP4(): return MP4Metadata(path=path, inner=inner)
            case mutagen.flac.FLAC(): return FLACMetadata(path=path, inner=inner)
            case mutagen.asf.ASF(): return WMAMetadata(path=path, inner=inner)
            case _: raise NotImplementedError(f"Unsupported metadata type {type(inner)}")

    @classmethod
    @abstractmethod
    def _init_once(cls): raise NotImplementedError()

    def __init__(self, path, inner):
        if self.__class__._first_instance:
            self.__class__._first_instance = False
            self.__class__._init_once(self.__class__)

        self._path = path
        self._inner = inner
        self._saved_tags = deepcopy(self._tags_as_dict())
        self.album_id = self.__class__.Accessor(
            self,
            self.__class__.ALBUM_ID_KEY)
        self.track_id = self.__class__.Accessor(
            self,
            self.__class__.TRACK_ID_KEY)

    @property
    def path(self): return self._path

    @property
    def inner(self): return self._inner

    @property
    def dirty(self):
        return self._tags_as_dict() != self._saved_tags

    @abstractmethod
    def _tags_as_dict(self): raise NotImplementedError()

    @abstractmethod
    def _scalar(self, key): raise NotImplementedError()

    def save(self):
        if self.dirty:
            if len(self._inner.tags) == 0:
                self._inner.delete()
            else:
                self._inner.save()
        self._m = None

    def pprint(self):
        return self._inner.pprint()

    def delete(self):
        self._inner.delete()
        self._m = None

    def get(self, key, default=_MISSING):
        if default is _MISSING:
            if self._inner.tags is None:
                raise KeyError(key)
        else:
            if self._inner.tags is None or key not in self._inner.tags:
                return default
        value = self._inner.tags[key]
        assert isinstance(value, list) and len(value) == 1
        return value[0]

    def set(self, key, value):
        if self._inner.tags is None:
            self._inner.add_tags()
        self._inner.tags[key] = value

    def pop(self, key, default=_MISSING):
        if default is _MISSING:
            if self._inner.tags is None:
                raise KeyError(key)
            return self._inner.tags.pop(key)
        else:
            if self._inner.tags is None:
                return default
            return self._inner.tags.pop(key, default)


class FLACMetadata(Metadata):
    COMMON_KEYS = CommonKeys(
        artist_title="albumartist",
        album_title="album",
        track_disc="discnumber",
        track_title="title",
        track_number="tracknumber",
        musicbrainz_artist_id="musicbrainz_artistid",
        musicbrainz_album_id="musicbrainz_albumid",
        musicbrainz_track_id="musicbrainz_trackid")

    def _init_once(cls): pass

    def _tags_as_dict(self):
        return self._inner.tags.as_dict()

    def _scalar(self, key):
        values = self._inner.tags.get(key, None)
        if values is None:
            return None
        assert isinstance(values, list) and len(values) == 1
        value = values[0]
        return value


class ID3Metadata(Metadata):
    COMMON_KEYS = CommonKeys(
        artist_title="artist",
        album_title="album",
        track_title="title",
        track_disc=Key(key="discnumber", func=parse_slash_number),
        track_number=Key(key="tracknumber", func=parse_slash_number),
        musicbrainz_artist_id="musicbrainz_artistid",
        musicbrainz_album_id="musicbrainz_albumid",
        musicbrainz_track_id="musicbrainz_trackid")

    def _init_once(cls):
        for key, id in [
            (cls.ALBUM_ID_KEY, "RCOOK_ALBUM_ID"),
            (cls.TRACK_ID_KEY, "RCOOK_TRACK_ID"),
        ]:
            EasyID3.RegisterTXXXKey(key, id)

    def _scalar(self, key):
        if self._inner.tags is None or key not in self._inner.tags:
            return None
        values = self._inner.tags[key]
        assert isinstance(values, list) and len(values) == 1
        value = values[0]
        return value

    def _tags_as_dict(self):
        return {} if self._inner.tags is None else dict(self._inner.tags)


class MP4Metadata(Metadata):
    COMMON_KEYS = CommonKeys(
        artist_title="artist",
        album_title="album",
        track_title="title",
        track_disc=Key(key="discnumber", func=parse_slash_number),
        track_number=Key(key="tracknumber", func=parse_slash_number),
        musicbrainz_artist_id="musicbrainz_artistid",
        musicbrainz_album_id="musicbrainz_albumid",
        musicbrainz_track_id="musicbrainz_trackid")

    def _init_once(cls):
        for key, id in [
            (cls.ALBUM_ID_KEY, "RCOOK_ALBUM_ID"),
            (cls.TRACK_ID_KEY, "RCOOK_TRACK_ID"),
        ]:
            EasyMP4Tags.RegisterFreeformKey(key, id, mean="org.rcook")

    def _tags_as_dict(self):
        return dict(self._inner.tags)

    def _scalar(self, key):
        values = self._inner.tags.get(key, None)
        if values is None:
            return None
        assert isinstance(values, list) and len(values) == 1
        value = values[0]
        return value


class WMAMetadata(Metadata):
    COMMON_KEYS = CommonKeys(
        artist_title="WM/AlbumArtist",
        album_title="WM/AlbumTitle",
        track_title="Title",
        track_disc=Key(key="WM/PartOfSet", func=parse_slash_number),
        track_number="WM/TrackNumber",
        musicbrainz_artist_id="MusicBrainz/Artist Id",
        musicbrainz_album_id="MusicBrainz/Album Id",
        musicbrainz_track_id="MusicBrainz/Track Id")

    def _init_once(cls): pass

    def _tags_as_dict(self):
        return dict(self._inner.tags)

    def _scalar(self, key):
        values = self._inner.tags.get(key, None)
        if values is None:
            return None
        assert isinstance(values, list) and len(values) == 1
        value = values[0].value
        return value
