from functools import partial
from mutagen.id3 import TALB, TIT2, TPE2, TPOS, TRCK, TXXX
from rtag.new_metadata import *


class MP3Metadata(Metadata):
    _MAPPINGS = [
        (ARTIST_TITLE_ATTR, "TPE2", TPE2, partial(TPE2, encoding=3)),
        (ALBUM_TITLE_ATTR, "TALB", TALB, partial(TALB, encoding=2)),
        (TRACK_TITLE_ATTR, "TIT2", TIT2, partial(TIT2, encoding=3)),
        (TRACK_DISC_ATTR, "TPOS", TPOS, partial(TPOS, encoding=3)),
        (TRACK_NUMBER_ATTR, "TRCK", TRCK, partial(TRCK, encoding=3)),
    ] + [
        (
            attr_name,
            f"TXXX:{key or attr_name.upper()}",
            TXXX,
            partial(TXXX, encoding=3, desc=key or attr_name.upper())
        )
        for attr_name, key in [
            (MUSICBRAINZ_ARTIST_ID_ATTR, "MusicBrainz Album Artist Id"),
            (MUSICBRAINZ_ALBUM_ID_ATTR, "MusicBrainz Album Id"),
            (MUSICBRAINZ_TRACK_ID_ATTR, "MusicBrainz Release Track Id"),
            (RCOOK_ARTIST_ID_ATTR, None),
            (RCOOK_ALBUM_ID_ATTR, None),
            (RCOOK_TRACK_ID_ATTR, None)
        ]
    ]
    _KEYS = {
        name: (key, tag_type, tag_ctor)
        for name, key, tag_type, tag_ctor in _MAPPINGS
    }
    _NAMES = {key: name for name, key, _, _ in _MAPPINGS}

    def get_tag(self, name, default=MISSING):
        key, tag_type, _ = self.__class__._KEYS[name]

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

    def set_tag(self, name, value):
        key, _, tag_ctor = self.__class__._KEYS[name]
        self._m.tags[key] = tag_ctor(text=value)

    def del_tag(self, name):
        key, _, _ = self.__class__._KEYS[name]
        del self._m.tags[key]
