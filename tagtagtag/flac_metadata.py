from tagtagtag.new_metadata import *


class FLACMetadata(Metadata):
    _MAPPINGS = [
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
    _KEYS = {name: key for name, key in _MAPPINGS}
    _NAMES = {key: name for name, key in _MAPPINGS}

    def get_tag(self, name, default=MISSING):
        key = self.__class__._KEYS[name]

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

    def set_tag(self, name, value):
        key = self.__class__._KEYS[name]
        self._m.tags[key] = value

    def del_tag(self, name):
        key = self.__class__._KEYS[name]
        del self._m.tags[key]
