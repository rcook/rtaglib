from abc import ABC, abstractmethod
from mutagen.id3 import TALB
from retagger.error import ReportableError
from uuid import UUID
import mutagen
import mutagen.asf
import mutagen.flac
import mutagen.mp3
import mutagen.mp4


class Metadata(ABC):
    def __init__(self, metadata):
        self._m = metadata

    @staticmethod
    def from_file(path):
        m = mutagen.File(path)
        match m:
            case mutagen.mp3.MP3(): return MP3Metadata(m)
            case mutagen.mp4.MP4(): return MP4Metadata(m)
            case mutagen.flac.FLAC(): return FLACMetadata(m)
            case mutagen.asf.ASF(): return WMAMetadata(m)
            case _: raise ReportableError(f"Unsupported metadata type ({type(m).__name__}) in file {path}")

    @property
    @abstractmethod
    def has_musicbrainz_metadata(self): raise NotImplementedError()

    @property
    @abstractmethod
    def album_id(self): raise NotImplementedError()

    @property
    @abstractmethod
    def album_title(self): raise NotImplementedError()

    @abstractmethod
    def set_album_title(self, value): raise NotImplementedError()

    @abstractmethod
    def _attr(self, key): raise NotImplementedError()

    def _uuid(self, key):
        s = self._attr(key)
        assert isinstance(s, str)
        return UUID(s)


class FLACMetadata(Metadata):
    @property
    def has_musicbrainz_metadata(self):
        return "musicbrainz_albumid" in self._m

    @property
    def album_id(self): return self._uuid("musicbrainz_albumid")

    @property
    def album_title(self): return self._attr("album")

    def set_album_title(self, value):
        self._m["album"] = value
        self._m.save()

    def _attr(self, key):
        entry = self._m[key]
        if len(entry) != 1:
            raise RuntimeError(f"Multivalued attribute {key} not supported")
        return entry[0]


class MP3Metadata(Metadata):
    @property
    def has_musicbrainz_metadata(self):
        return "TXXX:MusicBrainz Album Id" in self._m

    @property
    def album_id(self): return self._uuid("TXXX:MusicBrainz Album Id")

    @property
    def album_title(self): return self._attr("TALB")

    def set_album_title(self, value):
        self._m.tags.add(TALB(encoding=3, text=value))
        self._m.save()

    def _attr(self, key):
        entry = self._m[key].text
        if len(entry) != 1:
            raise RuntimeError(f"Multivalued attribute {key} not supported")

        return entry[0]


class MP4Metadata(Metadata):
    @property
    def has_musicbrainz_metadata(self):
        return "TXXX:MusicBrainz Album Id" in self._m

    @property
    def album_id(self): return self._uuid("TXXX:MusicBrainz Album Id")

    @property
    def album_title(self): return self._attr("TALB")

    def set_album_title(self, value):
        self._m.tags.add(TALB(encoding=3, text=value))
        self._m.save()

    def _attr(self, key):
        entry = self._m[key].text
        if len(entry) != 1:
            raise RuntimeError(f"Multivalued attribute {key} not supported")

        return entry[0]


class WMAMetadata(Metadata):
    @property
    def has_musicbrainz_metadata(self):
        return "MusicBrainz/Album Id" in self._m

    @property
    def album_id(self): return self._uuid("MusicBrainz/Album Id")

    @property
    def album_title(self): return self._attr("WM/AlbumTitle")

    def set_album_title(self, value):
        self._m["WM/AlbumTitle"] = value
        self._m.save()

    def _attr(self, key):
        entry = self._m[key]
        if len(entry) != 1:
            raise RuntimeError(f"Multivalued attribute {key} not supported")
        return entry[0].value
