from colorama import Fore
from itertools import takewhile
from pathlib import Path
from rpycli.fs import clean_dir
from rpycli.prelude import *
from rtag.album import Album
from rtag.artist import Artist
from rtag.file import File
from rtag.metadata.metadata import Metadata
from rtag.pos import Pos
from rtag.safe_str import make_safe_str
from rtag.track import Track
from time import sleep
import subprocess


def move_file(ctx, db, dry_run, source_path, target_path):
    def remove_dir_if_empty(dir):
        if len(list(dir.iterdir())) == 0:
            for i in range(0, 3):
                try:
                    dir.rmdir()
                    return
                except PermissionError:
                    sleep(0.5)

            if dir.is_dir():
                subprocess.run(["rd", "/s", "/q", str(dir)], shell=True)

            if dir.is_dir():
                ctx.log_warn(
                    f"Could not remove directory "
                    f"{dir} (probably locked by another process)")
            else:
                ctx.log_info(f"Removed directory {dir}")

    if source_path == target_path:
        ctx.log_info(f"No need to move {source_path}")
        return

    if dry_run:
        ctx.log_info(f"Would move {source_path} to {target_path}")
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(target_path)
        ctx.log_info(f"Moved {source_path} to {target_path}")
        remove_dir_if_empty(dir=source_path.parent)

    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE files
        SET path = ?
        WHERE path = ?
        """,
        (str(target_path), str(source_path), ))
    if cursor.rowcount != 1:
        raise RuntimeError(
            f"Failed to update file entry for \"{source_path}\"")
    if not dry_run:
        db.commit()


def do_retag(ctx, dry_run):
    def update_prefix(prefix, path):
        if prefix is None:
            return path.parent.parts
        comps = map(lambda p: p[0] == p[1], zip(prefix, path.parent.parts))
        new_prefix_len = len(list(takewhile(lambda p: p, comps)))
        return prefix[0:new_prefix_len]

    prefix = None
    with ctx.open_db() as db:
        for file in File.list(db=db):
            if not file.path.is_file():
                ctx.log_warning(f"File {file.path} not found")
                continue

            prefix = update_prefix(prefix, file.path)

            cprint(Fore.LIGHTCYAN_EX, f"Processing {file.key_path}")

            m = Metadata.load(file.path)

            if m.musicbrainz_track_id is not None:
                target_path = ctx.config.retagging.music_dir / \
                    Path(file.key_path)
                move_file(
                    ctx=ctx,
                    db=db,
                    dry_run=dry_run,
                    source_path=file.path,
                    target_path=target_path)
                continue

            artist = Artist.get_by_uuid(db=db, uuid=m.rcook_artist_id)
            album = Album.get_by_uuid(db=db, uuid=m.rcook_album_id)
            track = Track.get_by_uuid(db=db, uuid=m.rcook_track_id)

            disc_total = album.get_disc_total(db=db)
            track_total = album.get_track_total(db=db, disc=track.disc)

            if artist.disambiguator is None:
                artist_title = artist.title
                artist_part = artist.safe_title
            else:
                artist_title = f"{artist.title} ({artist.disambiguator})"
                artist_part = \
                    f"{artist.safe_title}_" \
                    f"{make_safe_str(artist.disambiguator)}"

            if album.disambiguator is None:
                album_title = album.title
                album_part = album.safe_title
            else:
                album_title = f"{album.title} ({album.disambiguator})"
                album_part = \
                    f"{album.safe_title}_" \
                    f"{make_safe_str(album.disambiguator)}"

            track_part = ""

            if disc_total == 1:
                del m.track_disc
            else:
                track_part += f"{track.disc}-"
                m.track_disc = Pos(index=track.disc, total=disc_total)

            if track.number is None:
                track_part += track.safe_title
                del m.track_number
            else:
                if track_total < 100:
                    track_number_str = f"{track.number:02}"
                elif track_total < 1000:
                    track_number_str = f"{track.number:03}"
                else:
                    track_number_str = f"{track.number:04}"
                track_part += f"{track_number_str}_{track.safe_title}"
                m.track_number = Pos(index=track.number, total=track_total)

            track_part += file.path.suffix.lower()

            m.artist_title = artist_title
            m.album_title = album_title
            m.track_title = track.title

            target_path = \
                ctx.config.retagging.misc_dir / \
                artist_part / album_part / track_part

            if not dry_run:
                m.save()

            move_file(
                ctx=ctx,
                db=db,
                dry_run=dry_run,
                source_path=file.path,
                target_path=target_path)

    # Earlier directory deletions don't always succeed, so let's try to clean up here...
    root_dir = Path(*prefix)
    if dry_run:
        ctx.log_info(f"Would attempt to clean up root directory {root_dir}")
    else:
        ctx.log_info(f"Attempting to clean up root directory {root_dir}")
        clean_dir(dir=root_dir, fail_ok=True)
