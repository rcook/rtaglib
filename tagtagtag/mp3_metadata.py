from functools import partial
from tagtagtag.new_metadata import *
from mutagen.id3 import TALB, TIT2, TPE2, TXXX


class MP3Metadata(Metadata):
    _MAPPINGS = [
        (ARTIST_TITLE_ATTR, "TPE2", TPE2, partial(TPE2, encoding=3)),
        (ALBUM_TITLE_ATTR, "TALB", TALB, partial(TALB, encoding=2)),
        (TRACK_TITLE_ATTR, "TIT2", TIT2, partial(TIT2, encoding=3)),
    ] + [
        (
            attr,
            f"TXXX:{attr.upper()}",
            TXXX,
            partial(TXXX, encoding=3, desc=attr.upper())
        )
        for attr in [RCOOK_ARTIST_ID_ATTR, RCOOK_ALBUM_ID_ATTR, RCOOK_TRACK_ID_ATTR]
    ]
    _KEYS = {
        name: (key, tag_type, tag_ctor)
        for name, key, tag_type, tag_ctor in _MAPPINGS
    }
    _NAMES = {key: name for name, key, _, _ in _MAPPINGS}

    def __init__(self, m):
        self._m = m

    def save(self):
        self._m.save()

    def pprint(self):
        return self._m.tags.pprint()

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
