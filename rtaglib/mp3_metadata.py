from functools import partial
from mutagen.id3 import TALB, TIT2, TPE2, TPOS, TRCK, TXXX, TextFrame
from rtaglib.metadata import \
    ALBUM_TITLE_ATTR, \
    ARTIST_TITLE_ATTR, \
    TRACK_TITLE_ATTR, \
    MISSING, \
    MUSICBRAINZ_ALBUM_ID_ATTR, \
    MUSICBRAINZ_ARTIST_ID_ATTR, \
    MUSICBRAINZ_TRACK_ID_ATTR, \
    RCOOK_ALBUM_ID_ATTR, \
    RCOOK_ARTIST_ID_ATTR, \
    RCOOK_TRACK_ID_ATTR, \
    Metadata
from rtaglib.pos import Pos
from typing import Any, Protocol, Sequence, Tuple


class TagCtor(Protocol):
    def __call__(self, text: str) -> object:
        raise NotImplementedError()


class MP3Metadata(Metadata):
    MAPPINGS: Sequence[Tuple[str, str, type[TextFrame], TagCtor]] = [
        (tag, tag_type.__name__, tag_type, partial(tag_type, encoding=3))
        for tag, tag_type in [
            (ARTIST_TITLE_ATTR, TPE2),
            (ALBUM_TITLE_ATTR, TALB),
            (TRACK_TITLE_ATTR, TIT2),
        ]
    ] + [
        (
            tag,
            f"TXXX:{key}",
            TXXX,
            partial(TXXX, encoding=3, desc=key)
        )
        for tag, key in [
            (MUSICBRAINZ_ARTIST_ID_ATTR, "MusicBrainz Album Artist Id"),
            (MUSICBRAINZ_ALBUM_ID_ATTR, "MusicBrainz Album Id"),
            (MUSICBRAINZ_TRACK_ID_ATTR, "MusicBrainz Release Track Id"),
            (RCOOK_ARTIST_ID_ATTR, "org.rcook/ArtistId"),
            (RCOOK_ALBUM_ID_ATTR, "org.rcook/AlbumId"),
            (RCOOK_TRACK_ID_ATTR, "org.rcook/TrackId")
        ]
    ]
    KEYS: dict[str, Tuple[str, type[TextFrame], TagCtor]] = {
        tag: (key, tag_type, tag_ctor)
        for tag, key, tag_type, tag_ctor in MAPPINGS
    }
    TAGS: dict[str, str] = {key: tag for tag, key, _, _ in MAPPINGS}

    def _get_tag(self, tag: str, default: Any = MISSING) -> Any:
        key, tag_type, _ = self.__class__.KEYS[tag]
        return self._get_raw(key=key, tag_type=tag_type, default=default)

    def _set_tag(self, tag: str, value: Any) -> None:
        key, _, tag_ctor = self.__class__.KEYS[tag]
        self._set_raw(key=key, tag_ctor=tag_ctor, value=str(value))

    def _del_tag(self, tag: str) -> None:
        self._del_raw(self.__class__.KEYS[tag][0])

    def _get_track_disc(self, default: Any = MISSING) -> Any:
        return self._get_pos(tag_type=TPOS, default=default)

    def _set_track_disc(self, value: Pos) -> None:
        self._set_pos(tag_type=TPOS, value=value)

    def _del_track_disc(self) -> None:
        self._del_raw(key=TPOS.__name__)

    def _get_track_number(self, default: Any = MISSING) -> Any:
        return self._get_pos(tag_type=TRCK, default=default)

    def _set_track_number(self, value: Pos) -> None:
        self._set_pos(tag_type=TRCK, value=value)

    def _del_track_number(self) -> None:
        self._del_raw(key=TRCK.__name__)

    def _get_raw(self, key: str, tag_type: type[TextFrame], default: Any = MISSING) -> Any:
        if default is MISSING:
            if self._m.tags is None:
                raise KeyError(key)
            item = self._m.tags[key]
        else:
            if self._m.tags is None:
                return default
            item = self._m.tags.get(key)
            if item is None:
                return default

        assert isinstance(item, tag_type)

        values = item.text  # type: ignore
        assert isinstance(values, list) and len(values) == 1

        value = values[0]
        assert isinstance(value, str)

        return value

    def _set_raw(self, key: str, tag_ctor: TagCtor, value: Any) -> None:
        if self._m.tags is None:
            self._m.add_tags()
            assert self._m.tags is not None
        self._m.tags[key] = tag_ctor(text=value)

    def _del_raw(self, key: str) -> None:
        if self._m.tags is not None:
            try:
                del self._m.tags[key]
            except KeyError:
                pass

    def _get_pos(self, tag_type: type[TextFrame], default: Any = MISSING) -> Pos | None:
        value = self._get_raw(
            key=tag_type.__name__,
            tag_type=tag_type,
            default=default if default is MISSING else None)
        match value:
            case None: return default
            case str(): return Pos.parse(value)
            case _: raise NotImplementedError()

    def _set_pos(self, tag_type: type[TextFrame], value: Any) -> None:
        self._set_raw(
            key=tag_type.__name__,
            tag_ctor=partial(tag_type, encoding=3),
            value=str(value))
