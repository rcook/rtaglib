from rtag.metadata.new_metadata import *


class WMAMetadata(Metadata):
    MAPPINGS = [
        (ARTIST_TITLE_ATTR, "WM/AlbumArtist"),
        (ALBUM_TITLE_ATTR, "WM/AlbumTitle"),
        (TRACK_TITLE_ATTR, "Title"),
        (TRACK_DISC_ATTR, "WM/PartOfSet"),
        (TRACK_NUMBER_ATTR, "WM/TrackNumber"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "MusicBrainz/Artist Id"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "MusicBrainz/Album Id"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "MusicBrainz/Track Id"),
        (RCOOK_ARTIST_ID_ATTR, "rcook_artist_id"),
        (RCOOK_ALBUM_ID_ATTR, "rcook_album_id"),
        (RCOOK_TRACK_ID_ATTR, "rcook_track_id")
    ]
    KEYS = {tag: key for tag, key in MAPPINGS}
    TAGS = {key: tag for tag, key in MAPPINGS}

    def _get_tag(self, tag, default=MISSING):
        key = self.__class__.KEYS[tag]

        if default is MISSING:
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

    def _set_tag(self, tag, value):
        key = self.__class__.KEYS[tag]
        self._m.tags[key] = value

    def _del_tag(self, tag):
        key = self.__class__.KEYS[tag]
        del self._m.tags[key]
