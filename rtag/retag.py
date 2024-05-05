from colorama import Fore
from rtag.album import Album
from rtag.artist import Artist
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.file import File
from rtag.fs import walk_dir
from rtag.metadata.metadata import Metadata
from rtag.pos import Pos
from rtag.safe_str import make_safe_str
from rtag.track import Track
from time import sleep
import subprocess


def move_file(ctx, db, dry_run, source_path, target_path):
    if dry_run:
        ctx.log_info(f"Would move {source_path} to {target_path}")
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT * FROM files
            WHERE path = ?
            """,
            source_path)
        for row in cursor.fetchall():
            print(row)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(target_path)
        ctx.log_info(f"Moved {source_path} to {target_path}")

        d = source_path.parent
        if len(list(d.iterdir())) > 0:
            return

        for i in range(0, 3):
            try:
                d.rmdir()
                return
            except PermissionError:
                sleep(0.5)

        if d.is_dir():
            subprocess.run(["rd", "/s", "/q", str(d)], shell=True)

        if d.is_dir():
            ctx.log_warn(
                f"Could not remove directory "
                f"{d} (probably locked by another process)")
        else:
            ctx.log_info(f"Removed directory {d}")


def do_retag(ctx, dry_run):
    with ctx.open_db() as db:
        for file in File.list(db=db):
            print(file.path)
        return
        for p in walk_dir(input_dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            rel_path = p.relative_to(input_dir)
            display_path = "/".join(rel_path.parts)
            cprint(Fore.LIGHTCYAN_EX, f"Processing {display_path}")

            m = Metadata.load(p)

            if m.musicbrainz_track_id is not None:
                target_path = music_dir / rel_path
                move_file(
                    ctx=ctx,
                    dry_run=dry_run,
                    source_path=p,
                    target_path=target_path)
                continue

            artist = Artist.get_by_uuid(db=db, uuid=m.rcook_artist_id)
            album = Album.get_by_uuid(db=db, uuid=m.rcook_album_id)
            track = Track.get_by_uuid(db=db, uuid=m.rcook_track_id)

            disc_total = album.get_disc_total(db=db)
            track_total = album.get_track_total(db=db)

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
                track_part += f"{track.number:02}_{track.safe_title}"
                m.track_number = Pos(index=track.number, total=track_total)

            track_part += p.suffix.lower()

            m.artist_title = artist_title
            m.album_title = album_title
            m.track_title = track.title

            target_path = misc_dir / artist_part / album_part / track_part

            if not dry_run:
                m.save()

            move_file(
                ctx=ctx,
                db=db,
                dry_run=dry_run,
                source_path=p,
                target_path=target_path)
