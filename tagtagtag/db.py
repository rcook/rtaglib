from pathlib import Path
# from tagtagtag.album import Album
# from tagtagtag.artist import Artist
from tagtagtag.fs import walk_dir
# from tagtagtag.track import Track
from tagtagtag.metadata import Metadata
from tagtagtag.metadata_db import MetadataDB
import os


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

            if m.title is None:
                print(f"File: {p.relative_to(d)}")
            else:
                print(f"Title: {m.title}")
            print(f"Number: {m.number}")
            print(f"Artist: {m.artist}")
            print(f"Album: {m.album}")
            print("-----")

    ctx.log_debug("do_db end")
