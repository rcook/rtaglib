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
from typing import Any, Sequence, Tuple


FREEFORM_PREFIX = "----:"


class MP4Metadata(Metadata):
    MAPPINGS: Sequence[Tuple[str, str]] = [
        (ARTIST_TITLE_ATTR, "aART"),
        (ALBUM_TITLE_ATTR, "\xa9alb"),
        (TRACK_TITLE_ATTR, "\xa9nam"),
        (MUSICBRAINZ_ARTIST_ID_ATTR, "musicbrainz_artistid"),
        (MUSICBRAINZ_ALBUM_ID_ATTR, "musicbrainz_albumid"),
        (MUSICBRAINZ_TRACK_ID_ATTR, "musicbrainz_trackid")
    ] + [
        (tag,  f"{FREEFORM_PREFIX}org.rcook:{label}")
        for tag, label in [
            (RCOOK_ARTIST_ID_ATTR, "ArtistId"),
            (RCOOK_ALBUM_ID_ATTR, "AlbumId"),
            (RCOOK_TRACK_ID_ATTR, "TrackId"),
        ]
    ]
    KEYS: dict[str, str] = {tag: key for tag, key in MAPPINGS}
    TAGS: dict[str, str] = {key: tag for tag, key in MAPPINGS}

    def _get_tag(self, tag: str, default: Any = MISSING) -> Any:
        return self._get_raw(self.__class__.KEYS[tag], default=default)

    def _set_tag(self, tag: str, value: Any) -> None:
        self._set_raw(key=self.__class__.KEYS[tag], value=str(value))

    def _del_tag(self, tag: str) -> None:
        self._del_raw(key=self.__class__.KEYS[tag])

    def _get_track_disc(self, default: Any = MISSING) -> Any:
        return self._get_pos("disk", default=default)

    def _set_track_disc(self, value: Pos) -> None:
        self._set_raw("disk", (value.index, value.total))

    def _del_track_disc(self) -> None:
        self._del_raw("disk")

    def _get_track_number(self, default: Any = MISSING) -> Any:
        return self._get_pos("trkn", default=default)

    def _set_track_number(self, value: Pos) -> None:
        self._set_raw("trkn", (value.index, value.total))

    def _del_track_number(self) -> None:
        self._del_raw("trkn")

    def _get_raw(self, key: str, default: Any = MISSING) -> Any:
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

    def _set_raw(self, key: str, value: Any) -> None:
        if key.startswith(FREEFORM_PREFIX):
            data = value.encode("utf-8")
        else:
            data = value
        if self._m.tags is None:
            self._m.add_tags()
            assert self._m.tags is not None
        self._m.tags[key] = [data]

    def _del_raw(self, key: str) -> None:
        try:
            del self._m.tags[key]
        except KeyError:
            pass

    def _get_pos(self, key: str, default: Any = MISSING) -> Any:
        value = self._get_raw(
            key,
            default=default if default is MISSING else None)
        match value:
            case None: return default
            case (int(index), int(total)): return Pos(index=index, total=total)
            case _: raise NotImplementedError()
