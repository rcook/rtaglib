from rtag.metadata.metadata import *


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

    def _get_tag(self, tag, default=UNSPECIFIED):
        return self._get_raw(key=self.__class__.KEYS[tag], default=default)

    def _set_tag(self, tag, value):
        self._set_raw(key=self.__class__.KEYS[tag], value=str(value))

    def _del_tag(self, tag):
        self._del_raw(key=self.__class__.KEYS[tag])

    def _get_track_disc(self, default=UNSPECIFIED):
        assert self._get_raw(key="disknumber", default=None) is None
        assert self._get_raw(key="totaldisks", default=None) is None
        assert self._get_raw(key="disctotal", default=None) \
            == self._get_raw(key="totaldiscs", default=None)
        return self._get_pos(
            index_key="discnumber",
            total_key="totaldiscs",
            default=default)

    def _set_track_disc(self, value):
        assert self._get_raw(key="disknumber", default=None) is None
        assert self._get_raw(key="totaldisks", default=None) is None
        self._set_pos(
            index_key="discnumber",
            total_key="totaldiscs",
            value=value)

    def _del_track_disc(self, default=UNSPECIFIED):
        self._del_raw(key="discnumber")
        self._del_raw(key="totaldiscs")

    def _get_track_number(self, default=UNSPECIFIED):
        assert self._get_raw(key="tracktotal", default=None) \
            == self._get_raw(key="totaltracks", default=None)
        return self._get_pos(index_key="tracknumber", total_key="totaltracks", default=default)

    def _set_track_number(self, value):
        self._set_pos(
            index_key="tracknumber",
            total_key="totaltracks",
            value=value)

    def _del_track_number(self, default=UNSPECIFIED):
        self._del_raw(key="tracknumber")
        self._del_raw(key="totaltracks")

    def _get_raw(self, key, default=UNSPECIFIED):
        if default is UNSPECIFIED:
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

    def _get_pos(self, index_key, total_key, default=UNSPECIFIED):
        index_str = self._get_raw(
            key=index_key,
            default=default if default is UNSPECIFIED else None)
        if index_str is None:
            return default

        total_str = self._get_raw(key=total_key, default=None)

        index = int(index_str)
        total = None if total_str is None else int(total_str)
        return Pos(index=index, total=total)

    def _set_pos(self, index_key, total_key, value):
        self._set_raw(key=index_key, value=str(value.index))
        if value.total is None:
            self._del_raw(key=total_key)
        else:
            self._set_raw(key=total_key, value=str(value.total))
