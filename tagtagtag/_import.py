from dataclasses import asdict, dataclass, fields
from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.error import ReportableError
from tagtagtag.fs import walk_dir
from tagtagtag.track import Track
from tagtagtag.metadata import Metadata
from tagtagtag.metadata_db import MetadataDB
import os
import re


_IGNORE_DIRS = {
    ".git",
    ".vscode",
    "__pycache__"
}


_INCLUDE_EXTS = {
    ".flac",
    ".m4a",
    ".mp3",
    ".wma"
}


_MUSICBRAINZ_ATTRS = [
    ("musicbrainz_artist_id", "MusicBrainz artist ID"),
    ("musicbrainz_album_id", "MusicBrainz album ID"),
    ("musicbrainz_track_id", "MusicBrainz track ID")
]


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
    title: str
    title_fs: str
    number: int
    artist: str
    artist_fs: str
    album: str
    album_fs: str

    _FILE_NAME_RE = re.compile("^(?P<digits>\\d+)(?P<rest>.+)$")

    @classmethod
    def parse(cls, rel_path):
        def humanize(s):
            return s.replace("_", " ").strip()

        parts = rel_path.parts
        if len(parts) < 3:
            raise ReportableError(
                f"File path \"{rel_path}\" does not match expected structure")

        artist_fs, album_fs, file_name = parts[-3:]

        name, _ = os.path.splitext(file_name)
        m = cls._FILE_NAME_RE.match(name)
        if m is None:
            number = None
            rest = name
        else:
            number = int(m.group("digits"))
            rest = m.group("rest").strip("_").strip()

        return cls(
            title=humanize(rest),
            title_fs=rest,
            number=number,
            artist=humanize(artist_fs),
            artist_fs=artist_fs,
            album=humanize(album_fs),
            album_fs=album_fs)


def do_import(ctx, data_dir, music_dir):
    db_path = data_dir / "metadata.db"
    ctx.log_debug("do_import begin")
    ctx.log_debug(f"db_path={db_path}")

    result = DBResult.default()
    with MetadataDB(db_path) as db:
        for p in walk_dir(music_dir, include_exts=_INCLUDE_EXTS, ignore_dirs=_IGNORE_DIRS):
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

    artist_title = inferred.artist if m.artist is None else m.artist
    assert artist_title is not None and len(artist_title) > 0

    album_title = inferred.album if m.album is None else m.album
    assert album_title is not None and len(album_title) > 0

    title = inferred.title if m.title is None else m.title
    assert title is not None and len(title) > 0

    number = inferred.number if m.number is None else m.number

    artist = Artist.query(db=db, name=artist_title, default=None)
    if artist is None:
        artist = Artist.create(
            db=db,
            name=artist_title,
            fs_name=inferred.artist_fs)
        ctx.log_info(f"New artist: {artist.name} ({artist.uuid})")
        result.new_artist_count += 1
    else:
        result.existing_artist_count += 1

    album = Album.query(
        db=db,
        artist_id=artist.id,
        name=album_title,
        default=None)
    if album is None:
        album = Album.create(
            db=db,
            artist_id=artist.id,
            name=album_title,
            fs_name=inferred.album_fs)
        ctx.log_info(f"New album: {album.name} ({album.uuid})")
        result.new_album_count += 1
    else:
        result.existing_album_count += 1

    track = Track.query(
        db=db,
        album_id=album.id,
        name=title,
        number=number,
        default=None)
    if track is None:
        track = Track.create(
            db=db,
            album_id=album.id,
            name=title,
            fs_name=inferred.title_fs,
            number=number)
        ctx.log_info(f"New track: {track.name} ({track.uuid})")
        result.new_track_count += 1
    else:
        result.existing_track_count += 1