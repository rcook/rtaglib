from abc import ABCMeta, abstractmethod
from functools import cached_property, partial
from rtag.index_of_total import IndexOfTotal
from uuid import UUID


MISSING = object()
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
    _ATTRS = [
        (ARTIST_TITLE_ATTR, str),
        (ALBUM_TITLE_ATTR, str),
        (TRACK_TITLE_ATTR, str),
        (TRACK_DISC_ATTR, IndexOfTotal.convert),
        (TRACK_NUMBER_ATTR, IndexOfTotal.convert),
        (MUSICBRAINZ_ARTIST_ID_ATTR, UUID),
        (MUSICBRAINZ_ALBUM_ID_ATTR, UUID),
        (MUSICBRAINZ_TRACK_ID_ATTR, UUID),
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
        from tagtagtag.flac_metadata import FLACMetadata
        from tagtagtag.mp3_metadata import MP3Metadata
        from tagtagtag.mp4_metadata import MP4Metadata
        from tagtagtag.wma_metadata import WMAMetadata
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
            case _: raise NotImplementedError(f"Unsupported metadata type {type(m)}")

    def __init__(self, m):
        self._m = m

    @cached_property
    def tags(self):
        return [attr_name for attr_name, _ in self.__class__._ATTRS]

    def save(self):
        self._m.save()

    def pprint(self):
        return self._m.tags.pprint()

    @abstractmethod
    def get_tag(self, name, default=MISSING): raise NotImplementedError()

    @abstractmethod
    def set_tag(self, name, value): raise NotImplementedError()

    @abstractmethod
    def del_tag(self, name): raise NotImplementedError()
