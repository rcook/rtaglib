from functools import partial
from mutagen.id3 import TALB, TIT2, TPE2, TPOS, TRCK, TXXX
from rtag.metadata.new_metadata import *


class MP3Metadata(Metadata):
    MAPPINGS = [
        (ARTIST_TITLE_ATTR, "TPE2", TPE2, partial(TPE2, encoding=3)),
        (ALBUM_TITLE_ATTR, "TALB", TALB, partial(TALB, encoding=2)),
        (TRACK_TITLE_ATTR, "TIT2", TIT2, partial(TIT2, encoding=3)),
        (TRACK_DISC_ATTR, "TPOS", TPOS, partial(TPOS, encoding=3)),
        (TRACK_NUMBER_ATTR, "TRCK", TRCK, partial(TRCK, encoding=3)),
    ] + [
        (
            tag,
            f"TXXX:{key or tag.upper()}",
            TXXX,
            partial(TXXX, encoding=3, desc=key or tag.upper())
        )
        for tag, key in [
            (MUSICBRAINZ_ARTIST_ID_ATTR, "MusicBrainz Album Artist Id"),
            (MUSICBRAINZ_ALBUM_ID_ATTR, "MusicBrainz Album Id"),
            (MUSICBRAINZ_TRACK_ID_ATTR, "MusicBrainz Release Track Id"),
            (RCOOK_ARTIST_ID_ATTR, None),
            (RCOOK_ALBUM_ID_ATTR, None),
            (RCOOK_TRACK_ID_ATTR, None)
        ]
    ]
    KEYS = {
        tag: (key, tag_type, tag_ctor)
        for tag, key, tag_type, tag_ctor in MAPPINGS
    }
    TAGS = {key: tag for tag, key, _, _ in MAPPINGS}

    def _get_tag(self, tag, default=MISSING):
        key, tag_type, _ = self.__class__.KEYS[tag]

        if default is MISSING:
            item = self._m.tags[key]
        else:
            item = self._m.tags.get(key)
            if item is None:
                return default

        assert isinstance(item, tag_type)

        values = item.text
        assert isinstance(values, list) and len(values) == 1

        value = values[0]
        assert isinstance(value, str)

        return value

    def _set_tag(self, tag, value):
        key, _, tag_ctor = self.__class__.KEYS[tag]
        self._m.tags[key] = tag_ctor(text=value)

    def _del_tag(self, tag):
        key, _, _ = self.__class__.KEYS[tag]
        del self._m.tags[key]
