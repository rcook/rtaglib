from tagtagtag.new_metadata import *


class MP4Metadata(Metadata):
    _MAPPINGS = [
        (ARTIST_TITLE_ATTR, "aART"),
        (ALBUM_TITLE_ATTR, "\xa9alb"),
        (TRACK_TITLE_ATTR, "\xa9nam"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "musicbrainz_artistid"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "musicbrainz_albumid"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "musicbrainz_trackid")
    ] + [
        (attr, f"----:org.rcook:{attr.upper()}")
        for attr in [RCOOK_ARTIST_ID_ATTR, RCOOK_ALBUM_ID_ATTR, RCOOK_TRACK_ID_ATTR]
    ]
    _KEYS = {name: key for name, key in _MAPPINGS}
    _NAMES = {key: name for name, key in _MAPPINGS}

    def get_tag(self, name, default=MISSING):
        key = self.__class__._KEYS[name]

        if default is MISSING:
            return self._m.tags[key]
        else:
            items = self._m.tags.get(key)
            if items is None:
                return default

        assert isinstance(items, list) and len(items) == 1

        item = items[0]
        if isinstance(item, str):
            return item

        value = item.decode()
        assert isinstance(value, str)

        return value

    def set_tag(self, name, value):
        key = self.__class__._KEYS[name]
        self._m.tags[key] = value

    def del_tag(self, name):
        key = self.__class__._KEYS[name]
        del self._m.tags[key]
