from dataclasses import asdict, dataclass, fields
from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from tagtagtag.error import ReportableError
from tagtagtag.fs import walk_dir
from tagtagtag.safe_str import humanize_str, make_safe_str
from tagtagtag.track import Track
from tagtagtag.metadata import Metadata
from tagtagtag.metadata_db import MetadataDB
import os
import re


"""
_MUSICBRAINZ_ATTRS = [
    ("musicbrainz_artist_id", "MusicBrainz artist ID"),
    ("musicbrainz_album_id", "MusicBrainz album ID"),
    ("musicbrainz_track_id", "MusicBrainz track ID")
]
"""


@dataclass
class DBResult:
    total: int
    skipped_count: int
    new_artist_count: int
    existing_artist_count: int
    new_album_count: int
    existing_album_count: int
    new_track_count: int
    existing_track_count: int

    @classmethod
    def default(cls):
        return cls(**{f.name: 0 for f in fields(cls)})


@dataclass(frozen=True)
class InferredInfo:
    artist_title: str
    artist_safe_title: str
    album_title: str
    album_safe_title: str
    track_title: str
    track_safe_title: str
    track_number: int

    _FILE_NAME_RE = re.compile("^(?P<digits>\\d+)(?P<rest>.+)$")

    @classmethod
    def parse(cls, rel_path):
        parts = rel_path.parts
        if len(parts) < 3:
            raise ReportableError(
                f"File path \"{rel_path}\" does not match expected structure")

        artist_safe_title, album_safe_title, file_name = parts[-3:]

        base_file_name, _ = os.path.splitext(file_name)
        m = cls._FILE_NAME_RE.match(base_file_name)
        if m is None:
            track_number = None
            track_safe_title = base_file_name
        else:
            track_number = int(m.group("digits"))
            track_safe_title = m.group("rest").lstrip("_").lstrip(" ")

        return cls(
            artist_title=humanize_str(artist_safe_title),
            artist_safe_title=artist_safe_title,
            album_title=humanize_str(album_safe_title),
            album_safe_title=album_safe_title,
            track_title=humanize_str(track_safe_title),
            track_safe_title=track_safe_title,
            track_number=track_number)


def do_import(ctx, data_dir, music_dir, init=False):
    db_path = data_dir / "metadata.db"
    ctx.log_debug("do_import begin")
    ctx.log_debug(f"db_path={db_path}")

    if init and db_path.is_file():
        db_path.unlink()

    result = DBResult.default()

    with MetadataDB(db_path) as db:
        for p in walk_dir(music_dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            result.total += 1
            m = Metadata.load(p)
            if m.musicbrainz_track_id is None:
                process_file(
                    ctx=ctx,
                    result=result,
                    dir=music_dir,
                    path=p,
                    m=m,
                    db=db)
            else:
                result.skipped_count += 1

    for k, v in asdict(result).items():
        ctx.log_info(f"{k}={v}")

    ctx.log_debug("do_import end")


def process_file(ctx, result, dir, path, m, db):
    rel_path = path.relative_to(dir)
    inferred = InferredInfo.parse(rel_path)

    def get_titles(key):
        temp = getattr(m, key)
        if temp is None:
            return getattr(inferred, key), getattr(inferred, key.replace("title", "safe_title"))
        else:
            return temp, make_safe_str(temp)

    artist_title, artist_safe_title = get_titles("artist_title")
    album_title, album_safe_title = get_titles("album_title")
    track_title, track_safe_title = get_titles("track_title")
    track_number = inferred.track_number if m.track_number is None else m.track_number

    artist = Artist.query(db=db, title=artist_title, default=None)
    if artist is None:
        artist = Artist.create(
            db=db,
            title=artist_title,
            safe_title=artist_safe_title)
        ctx.log_info(f"New artist: {artist.title} ({artist.uuid})")
        result.new_artist_count += 1
    else:
        result.existing_artist_count += 1

    album = Album.query(
        db=db,
        artist_id=artist.id,
        title=album_title,
        default=None)
    if album is None:
        album = Album.create(
            db=db,
            artist_id=artist.id,
            title=album_title,
            safe_title=album_safe_title)
        ctx.log_info(f"New album: {album.title} ({album.uuid})")
        result.new_album_count += 1
    else:
        result.existing_album_count += 1

    track = Track.query(
        db=db,
        album_id=album.id,
        title=track_title,
        number=track_number,
        default=None)
    if track is None:
        track = Track.create(
            db=db,
            album_id=album.id,
            title=track_title,
            safe_title=track_safe_title,
            number=track_number)
        ctx.log_info(f"New track: {track.title} ({track.uuid})")
        result.new_track_count += 1
    else:
        result.existing_track_count += 1
