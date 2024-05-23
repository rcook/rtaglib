from dataclasses import dataclass
from rtaglib.metadata import \
    ALBUM_TITLE_ATTR, \
    ARTIST_TITLE_ATTR, \
    TRACK_TITLE_ATTR, \
    MISSING, \
    MUSICBRAINZ_ALBUM_ID_ATTR, \
    MUSICBRAINZ_ARTIST_ID_ATTR, \
    MUSICBRAINZ_TRACK_ID_ATTR, \
    RCOOK_ALBUM_ID_ATTR, \
    RCOOK_ARTIST_ID_ATTR, \
    RCOOK_TRACK_ID_ATTR, \
    Metadata
from rtaglib.pos import Pos


class FLACMetadata(Metadata):
    MAPPINGS = [
        (ARTIST_TITLE_ATTR, "albumartist"),
        (ALBUM_TITLE_ATTR, "album"),
        (TRACK_TITLE_ATTR, "title"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "musicbrainz_artistid"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "musicbrainz_albumid"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "musicbrainz_trackid"),
        (RCOOK_ARTIST_ID_ATTR, "rcook_artist_id"),
        (RCOOK_ALBUM_ID_ATTR, "rcook_album_id"),
        (RCOOK_TRACK_ID_ATTR, "rcook_track_id")
    ]
    KEYS = {tag: key for tag, key in MAPPINGS}
    TAGS = {key: tag for tag, key in MAPPINGS}

    @dataclass(frozen=True)
    class PosTag:
        obj: object
        index_key: str
        other_index_keys: list[str]
        total_key: str
        other_total_keys: list[str]

        def get(self, default):
            index_str = self.obj._get_raw(
                key=self.index_key,
                default=default if default is MISSING else None)
            for k in self.other_index_keys:
                s = self.obj._get_raw(key=k, default=None)
                assert s is None or s == index_str

            if index_str is None:
                return default

            total_str = self.obj._get_raw(key=self.total_key, default=None)
            for k in self.other_total_keys:
                s = self.obj._get_raw(key=k, default=None)
                assert s is None or s == total_str

            index = int(index_str)
            total = None if total_str is None else int(total_str)
            return Pos(index=index, total=total)

        def set(self, value):
            s = str(value.index)
            for k in [self.index_key] + self.other_index_keys:
                self.obj._set_raw(key=k, value=s)

            s = str(value.total)
            for k in [self.total_key] + self.other_total_keys:
                if value.total is None:
                    self.obj._del_raw(key=k)
                else:
                    self.obj._set_raw(key=k, value=s)

        def delete(self):
            for k in [self.index_key, self.total_key] + self.other_index_keys + self.other_total_keys:
                self.obj._del_raw(key=k)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._track_disc = self.__class__.PosTag(
            obj=self,
            index_key="discnumber",
            other_index_keys=[],
            total_key="totaldiscs",
            other_total_keys=["disctotal"])
        self._track_number = self.__class__.PosTag(
            obj=self,
            index_key="tracknumber",
            other_index_keys=[],
            total_key="totaltracks",
            other_total_keys=["tracktotal"])

    def _get_tag(self, tag, default=MISSING):
        return self._get_raw(key=self.__class__.KEYS[tag], default=default)

    def _set_tag(self, tag, value):
        self._set_raw(key=self.__class__.KEYS[tag], value=str(value))

    def _del_tag(self, tag):
        self._del_raw(key=self.__class__.KEYS[tag])

    def _get_track_disc(self, default=MISSING):
        return self._track_disc.get(default=default)

    def _set_track_disc(self, value):
        self._track_disc.set(value=value)

    def _del_track_disc(self):
        self._track_disc.delete()

    def _get_track_number(self, default=MISSING):
        return self._track_number.get(default=default)

    def _set_track_number(self, value):
        self._track_number.set(value=value)

    def _del_track_number(self):
        self._track_number.delete()

    def _get_raw(self, key, default=MISSING):
        if default is MISSING:
            return self._m.tags[key]
        else:
            values = self._m.tags.get(key)
            if values is None:
                return default

        assert isinstance(values, list) and len(values) == 1

        value = values[0]
        assert isinstance(value, str)

        return value

    def _set_raw(self, key, value):
        self._m.tags[key] = value

    def _del_raw(self, key):
        try:
            del self._m.tags[key]
        except KeyError:
            pass
