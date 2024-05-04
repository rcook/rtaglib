from functools import partial
from mutagen.id3 import TALB, TIT2, TPE2, TPOS, TRCK, TXXX
from rtag.metadata.metadata import *


class MP3Metadata(Metadata):
    MAPPINGS = [
        (tag, tag_type.__name__, tag_type, partial(tag_type, encoding=3))
        for tag, tag_type in [
            (ARTIST_TITLE_ATTR, TPE2),
            (ALBUM_TITLE_ATTR, TALB),
            (TRACK_TITLE_ATTR, TIT2),
        ]
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

    def _get_tag(self, tag, default=UNSPECIFIED):
        key, tag_type, _ = self.__class__.KEYS[tag]
        return self._get_raw(key=key, tag_type=tag_type, default=default)

    def _set_tag(self, tag, value):
        key, _, tag_ctor = self.__class__.KEYS[tag]
        self._set_raw(key=key, tag_ctor=tag_ctor, value=str(value))

    def _del_tag(self, tag):
        self._del_raw(self.__class__.KEYS[tag][0])

    def _get_track_disc(self, default=UNSPECIFIED):
        return self._get_pos(tag_type=TPOS, default=default)

    def _set_track_disc(self, value):
        self._set_pos(tag_type=TPOS, value=value)

    def _del_track_disc(self):
        self._del_raw(key=TPOS.__name__)

    def _get_track_number(self, default=UNSPECIFIED):
        return self._get_pos(tag_type=TRCK, default=default)

    def _set_track_number(self, value):
        self._set_pos(tag_type=TRCK, value=value)

    def _del_track_number(self):
        self._del_raw(key=TRCK.__name__)

    def _get_raw(self, key, tag_type, default=UNSPECIFIED):
        if default is UNSPECIFIED:
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

    def _set_raw(self, key, tag_ctor, value):
        self._m.tags[key] = tag_ctor(text=value)

    def _del_raw(self, key):
        try:
            del self._m.tags[key]
        except KeyError:
            pass

    def _get_pos(self, tag_type, default=UNSPECIFIED):
        value = self._get_raw(
            key=tag_type.__name__,
            tag_type=tag_type,
            default=default if default is UNSPECIFIED else None)
        match value:
            case None: return default
            case str(): return Pos.parse(value)
            case _: raise NotImplementedError()

    def _set_pos(self, tag_type, value):
        self._set_raw(
            key=tag_type.__name__,
            tag_ctor=partial(tag_type, encoding=3),
            value=str(value))
