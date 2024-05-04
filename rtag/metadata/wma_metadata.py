from rtag.metadata.new_metadata import *


class WMAMetadata(Metadata):
    MAPPINGS = [
        (ARTIST_TITLE_ATTR, "WM/AlbumArtist"),
        (ALBUM_TITLE_ATTR, "WM/AlbumTitle"),
        (TRACK_TITLE_ATTR, "Title"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "MusicBrainz/Artist Id"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "MusicBrainz/Album Id"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "MusicBrainz/Track Id"),
        (RCOOK_ARTIST_ID_ATTR, "rcook_artist_id"),
        (RCOOK_ALBUM_ID_ATTR, "rcook_album_id"),
        (RCOOK_TRACK_ID_ATTR, "rcook_track_id")
    ]
    KEYS = {tag: key for tag, key in MAPPINGS}
    TAGS = {key: tag for tag, key in MAPPINGS}

    def _get_tag(self, tag, default=UNSPECIFIED):
        return self._get_raw(key=self.__class__.KEYS[tag], default=default)

    def _set_tag(self, tag, value):
        self._set_raw(key=self.__class__.KEYS[tag], value=value)

    def _del_tag(self, tag):
        self._del_raw(key=self.__class__.KEYS[tag])

    def _get_track_disc(self, default=UNSPECIFIED):
        return self._get_pos(key="WM/PartOfSet", default=default)

    def _set_track_disc(self, value):
        self._set_pos(key="WM/PartOfSet", value=value)

    def _del_track_disc(self):
        self._del_raw(key="WM/PartOfSet")

    def _get_track_number(self, default=UNSPECIFIED):
        return self._get_pos(key="WM/TrackNumber", default=default)

    def _set_track_number(self, value):
        self._set_pos(key="WM/TrackNumber", value=value)

    def _del_track_number(self):
        self._del_raw(key="WM/TrackNumber")

    def _get_raw(self, key, default=UNSPECIFIED):
        if default is UNSPECIFIED:
            items = self._m.tags[key]
        else:
            items = self._m.tags.get(key)
            if items is None:
                return default

        assert isinstance(items, list) and len(items) == 1

        item = items[0]
        value = item.value
        if isinstance(value, int):
            return value
        else:
            assert isinstance(value, str)
            return value

    def _set_raw(self, key, value):
        self._m.tags[key] = value

    def _del_raw(self, key):
        try:
            del self._m.tags[key]
        except KeyError:
            pass

    def _get_pos(self, key, default=UNSPECIFIED):
        value = self._get_raw(
            key=key,
            default=default if default is UNSPECIFIED else None)
        match value:
            case None: return default
            case int(): return Pos(index=value, total=None)
            case str(): return Pos.parse(value)
            case _: raise NotImplementedError()

    def _set_pos(self, key, value):
        self._set_raw(key=key, value=str(value))
