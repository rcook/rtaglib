from tagtagtag.new_metadata import *


class WMAMetadata(Metadata):
    _MAPPINGS = [
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
    _KEYS = {name: key for name, key in _MAPPINGS}
    _NAMES = {key: name for name, key in _MAPPINGS}

    def get_tag(self, name, default=MISSING):
        key = self.__class__._KEYS[name]

        if default is MISSING:
            items = self._m.tags[key]
        else:
            items = self._m.tags.get(key)
            if items is None:
                return default

        assert isinstance(items, list) and len(items) == 1

        item = items[0]
        value = item.value
        assert isinstance(value, str)

        return value

    def set_tag(self, name, value):
        key = self.__class__._KEYS[name]
        self._m.tags[key] = value

    def del_tag(self, name):
        key = self.__class__._KEYS[name]
        del self._m.tags[key]
