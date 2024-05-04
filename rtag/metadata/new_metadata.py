from abc import ABCMeta, abstractmethod
from functools import cached_property, partial
from rtag.position import Position
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
    _TAGS = [
        (ARTIST_TITLE_ATTR, str),
        (ALBUM_TITLE_ATTR, str),
        (TRACK_TITLE_ATTR, str),
        (TRACK_DISC_ATTR, Position.convert),
        (TRACK_NUMBER_ATTR, Position.convert),
        (MUSICBRAINZ_ARTIST_ID_ATTR, UUID),
        (MUSICBRAINZ_ALBUM_ID_ATTR, UUID),
        (MUSICBRAINZ_TRACK_ID_ATTR, UUID),
        (RCOOK_ARTIST_ID_ATTR, UUID),
        (RCOOK_ALBUM_ID_ATTR, UUID),
        (RCOOK_TRACK_ID_ATTR, UUID)
    ]
    _TO_TYPES = {tag: tag_type for tag, tag_type in _TAGS}

    def __new__(cls, name, bases, dct):
        def fget(tag, self):
            return self.get_tag(tag, default=None)

        def fset(tag, self, value):
            return self.set_tag(tag, value)

        def fdel(tag, self):
            return self.del_tag(tag)

        t = super().__new__(cls, name, bases, dct)
        for tag, _ in cls._TAGS:
            setattr(
                t,
                tag,
                property(
                    partial(fget, tag),
                    partial(fset, tag),
                    partial(fdel, tag)))
        return t


class Metadata(metaclass=MetadataMeta):
    @staticmethod
    def load(path):
        from rtag.metadata.flac_metadata import FLACMetadata
        from rtag.metadata.mp3_metadata import MP3Metadata
        from rtag.metadata.mp4_metadata import MP4Metadata
        from rtag.metadata.wma_metadata import WMAMetadata
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
        return [tag for tag, _ in self.__class__._TAGS]

    @property
    def raw_tags(self):
        return self._m.tags.keys()

    def save(self):
        self._m.save()

    def pprint(self):
        return self._m.tags.pprint()

    def get_tag(self, tag, default=MISSING):
        tag_type = self.__class__._TO_TYPES[tag]
        value = self._get_tag(tag, default=default)
        return None if value is None else tag_type(value)

    def set_tag(self, tag, value):
        return self._set_tag(tag, str(value))

    def del_tag(self, tag):
        return self._del_tag(tag)

    @abstractmethod
    def _get_tag(self, name, default=MISSING): raise NotImplementedError()

    @abstractmethod
    def _set_tag(self, name, value): raise NotImplementedError()

    @abstractmethod
    def _del_tag(self, name): raise NotImplementedError()
