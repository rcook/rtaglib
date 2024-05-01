from abc import ABC, abstractmethod
from copy import deepcopy
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4Tags
import mutagen
import mutagen.asf
import mutagen.easyid3
import mutagen.easymp4
import mutagen.flac
import mutagen.id3
import mutagen.mp3


MISSING_ARG = object()


class Metadata(ABC):
    ALBUM_ID_KEY = "rcook_album_id"
    TRACK_ID_KEY = "rcook_track_id"
    _first_instance = True

    class Accessor:
        def __init__(self, metadata, key):
            self._metadata = metadata
            self._key = key

        def get(self, default=MISSING_ARG):
            return self._metadata.get(key=self._key, default=default)

        def set(self, value):
            self._metadata.set(key=self._key, value=value)

        def pop(self, default=MISSING_ARG):
            self._metadata.pop(key=self._key, default=default)

    @staticmethod
    def load(path):
        inner = mutagen.File(path, easy=True)
        match inner:
            case mutagen.mp3.EasyMP3(): return ID3Metadata(path, inner)
            case mutagen.easymp4.EasyMP4(): return MP4Metadata(path, inner)
            case mutagen.flac.FLAC(): return FLACMetadata(path, inner)
            case mutagen.asf.ASF(): return WMAMetadata(path, inner)
            case _: raise NotImplementedError(f"Unsupported metadata type {type(tags)}")

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
    def inner(self): return self._inner

    @property
    def dirty(self):
        return self._tags_as_dict() != self._saved_tags

    @abstractmethod
    def _tags_as_dict(self): raise NotImplementedError()

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

    def get(self, key, default=MISSING_ARG):
        if default is MISSING_ARG:
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

    def pop(self, key, default=MISSING_ARG):
        if default is MISSING_ARG:
            if self._inner.tags is None:
                raise KeyError(key)
            return self._inner.tags.pop(key)
        else:
            if self._inner.tags is None:
                return default
            return self._inner.tags.pop(key, default)


class FLACMetadata(Metadata):
    def _init_once(cls): pass

    def _tags_as_dict(self):
        return self._inner.tags.as_dict()


class ID3Metadata(Metadata):
    KEYS = [
        (Metadata.ALBUM_ID_KEY, "RCOOK_ALBUM_ID"),
        (Metadata.TRACK_ID_KEY, "RCOOK_TRACK_ID"),
    ]

    def _init_once(cls):
        for key, id in cls.KEYS:
            EasyID3.RegisterTXXXKey(key, id)

    def _tags_as_dict(self):
        return {} if self._inner.tags is None else dict(self._inner.tags)


class MP4Metadata(Metadata):
    KEYS = [
        (Metadata.ALBUM_ID_KEY, "RCOOK_ALBUM_ID"),
        (Metadata.TRACK_ID_KEY, "RCOOK_TRACK_ID"),
    ]

    def _init_once(cls):
        for key, id in cls.KEYS:
            EasyMP4Tags.RegisterFreeformKey(key, id, mean="org.rcook")

    def _tags_as_dict(self):
        return dict(self._inner.tags)


class WMAMetadata(Metadata):
    def _init_once(cls): pass

    def _tags_as_dict(self):
        return dict(self._inner.tags)
