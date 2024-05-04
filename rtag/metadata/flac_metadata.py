from rtag.metadata.new_metadata import *


class FLACMetadata(Metadata):
    MAPPINGS = [
        (ARTIST_TITLE_ATTR, "albumartist"),
        (ALBUM_TITLE_ATTR, "album"),
        (TRACK_TITLE_ATTR, "title"),
        (TRACK_DISC_ATTR, "discnumber"),
        (TRACK_NUMBER_ATTR, "tracknumber"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "musicbrainz_artistid"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "musicbrainz_albumid"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "musicbrainz_trackid"),
        (RCOOK_ARTIST_ID_ATTR, "rcook_artist_id"),
        (RCOOK_ALBUM_ID_ATTR, "rcook_album_id"),
        (RCOOK_TRACK_ID_ATTR, "rcook_track_id")
    ]
    KEYS = {tag: key for tag, key in MAPPINGS}
    TAGS = {key: tag for tag, key in MAPPINGS}

    def _get_tag(self, tag, default=MISSING):
        key = self.__class__.KEYS[tag]

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

    def _set_tag(self, tag, value):
        key = self.__class__.KEYS[tag]
        self._m.tags[key] = value

    def _del_tag(self, tag):
        key = self.__class__.KEYS[tag]
        del self._m.tags[key]
