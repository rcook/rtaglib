from rtag.metadata.new_metadata import *


class MP4Metadata(Metadata):
    MAPPINGS = [
        (ARTIST_TITLE_ATTR, "aART"),
        (ALBUM_TITLE_ATTR, "\xa9alb"),
        (TRACK_TITLE_ATTR, "\xa9nam"),
        (TRACK_DISC_ATTR, "disk"),
        (TRACK_NUMBER_ATTR, "trkn"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "musicbrainz_artistid"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "musicbrainz_albumid"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "musicbrainz_trackid")
    ] + [
        (attr, f"----:org.rcook:{attr.upper()}")
        for attr in [RCOOK_ARTIST_ID_ATTR, RCOOK_ALBUM_ID_ATTR, RCOOK_TRACK_ID_ATTR]
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
        if isinstance(item, str):
            return item

        if isinstance(item, tuple):
            return item

        value = item.decode()
        assert isinstance(value, str)

        return value

    def _set_tag(self, tag, value):
        key = self.__class__.KEYS[tag]
        self._m.tags[key] = value

    def _del_tag(self, tag):
        key = self.__class__.KEYS[tag]
        del self._m.tags[key]
