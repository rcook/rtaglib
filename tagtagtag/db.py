from dataclasses import dataclass
from pathlib import Path
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


@dataclass(frozen=True)
class InferredInfo:
    title: str
    title_fs: str
    number: int
    artist: str
    artist_fs: str
    album: str
    album_fs: str

    _FILE_NAME_RE = re.compile("^(?P<digits>\d+)(?P<rest>.+)$")

    @classmethod
    def parse(cls, rel_path):
        def humanize(s):
            return s.replace("_", " ").strip()

        parts = rel_path.parts
        if len(parts) != 3:
            raise ReportableError(
                f"File path \"{rel_path}\" does not match expected structure")

        artist_fs, album_fs, file_name = parts

        name, _ = os.path.splitext(file_name)
        m = cls._FILE_NAME_RE.match(name)
        if m is None:
            number = None
            rest = name
        else:
            number = int(m.group("digits"))
            rest = m.group("rest")

        return cls(
            title=humanize(rest),
            title_fs=file_name,
            number=number,
            artist=humanize(artist_fs),
            artist_fs=artist_fs,
            album=humanize(album_fs),
            album_fs=album_fs)


def do_db(ctx, data_dir):
    db_path = data_dir / "metadata.db"
    ctx.log_debug("do_db begin")
    ctx.log_debug(f"db_path={db_path}")

    with MetadataDB(db_path) as db:
        """
        artist = Artist.query(db=db, name="From the Fall", default=None)
        if artist is None:
            artist = Artist.create(
                db=db,
                name="From the Fall",
                fs_name="From_the_Fall")
        ctx.log_info(artist)

        album = Album.query(
            db=db,
            artist_id=artist.id,
            name="Entropy",
            default=None)
        if album is None:
            album = Album.create(
                db=db,
                artist_id=artist.id,
                name="Entropy",
                fs_name="Entropy")
        ctx.log_info(album)

        track = Track.query(
            db=db,
            album_id=album.id,
            name="Armed and Hammered",
            number=1)
        if track is None:
            track = Track.create(
                db=db,
                album_id=album.id,
                name="Armed and Hammered",
                fs_name="Armed_and_Hammered",
                number=1)
        ctx.log_info(track)
        """
        d = Path(os.getenv("USERPROFILE")) / \
            "Desktop" / \
            "Beets" / \
            "Scratch.bak"
        for p in walk_dir(d, include_exts=_INCLUDE_EXTS, ignore_dirs=_IGNORE_DIRS):
            m = Metadata.load(p)
            if m.musicbrainz_track_id is not None:
                continue

            rel_path = p.relative_to(d)
            inferred = InferredInfo.parse(rel_path)

            artist_name = inferred.artist if m.artist is None else m.artist
            assert artist_name is not None and len(artist_name) > 0

            album_name = inferred.artist if m.album is None else m.album
            assert album_name is not None and len(album_name) > 0

            title = inferred.title if m.title is None else m.title
            assert title is not None and len(title) > 0

            number = inferred.number if m.number is None else m.number

            artist = Artist.query(db=db, name=artist_name, default=None)
            if artist is None:
                artist = Artist.create(
                    db=db,
                    name=artist_name,
                    fs_name=inferred.artist_fs)
                ctx.log_info(f"New artist: {artist.name} ({artist.uuid})")
            else:
                ctx.log_info(f"Existing artist: {artist.name} ({artist.uuid})")

    ctx.log_debug("do_db end")
