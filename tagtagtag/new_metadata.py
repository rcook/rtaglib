from abc import ABCMeta, abstractmethod
from functools import cached_property, partial
from uuid import UUID
import mutagen
import mutagen.mp3


MISSING = object()
ARTIST_TITLE_ATTR = "artist_title"
ALBUM_TITLE_ATTR = "album_title"
TRACK_TITLE_ATTR = "track_title"
RCOOK_ARTIST_ID_ATTR = "rcook_artist_id"
RCOOK_ALBUM_ID_ATTR = "rcook_album_id"
RCOOK_TRACK_ID_ATTR = "rcook_track_id"


class MetadataMeta(ABCMeta):
    _ATTRS = [
        (ARTIST_TITLE_ATTR, str),
        (ALBUM_TITLE_ATTR, str),
        (TRACK_TITLE_ATTR, str),
        (RCOOK_ARTIST_ID_ATTR, UUID),
        (RCOOK_ALBUM_ID_ATTR, UUID),
        (RCOOK_TRACK_ID_ATTR, UUID)
    ]

    def __new__(cls, name, bases, dct):
        def fget(attr_name, attr_type, self):
            value = self.get_tag(attr_name, default=None)
            return None if value is None else attr_type(value)

        def fset(attr_name, self, value):
            return self.set_tag(attr_name, str(value))

        def fdel(attr_name, self):
            return self.del_tag(attr_name)

        t = super().__new__(cls, name, bases, dct)
        for attr_name, attr_type in cls._ATTRS:
            setattr(
                t,
                attr_name,
                property(
                    partial(fget, attr_name, attr_type),
                    partial(fset, attr_name),
                    partial(fdel, attr_name)))
        return t


class Metadata(metaclass=MetadataMeta):
    @staticmethod
    def load(path):
        from tagtagtag.mp3_metadata import MP3Metadata
        m = mutagen.File(path)
        match m:
            case mutagen.mp3.MP3(): return MP3Metadata(m=m)
            case _: raise NotImplementedError(f"Unsupported metadata type {type(m)}")

    @cached_property
    def tags(self):
        return [attr_name for attr_name, _ in self.__class__._ATTRS]

    @abstractmethod
    def save(self): raise NotImplementedError()

    @abstractmethod
    def pprint(self): raise NotImplementedError()

    @abstractmethod
    def get_tag(self, name, default=MISSING): raise NotImplementedError()

    @abstractmethod
    def set_tag(self, name, value): raise NotImplementedError()

    @abstractmethod
    def del_tag(self, name): raise NotImplementedError()
