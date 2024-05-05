from rtag.file import File
from rtag.ui import banner, confirm, select_artist, select_track, show_item


def do_delete_artist(ctx):
    banner("delete artist")

    with ctx.open_db() as db:
        artist = select_artist(db=db)
        show_item(artist)
        confirm(ctx=ctx, prompt="Do you wish to delete this artist and all associated albums and tracks from the database?")

        cursor = db.cursor()

        cursor.execute(
            """
            DELETE FROM files
            WHERE artist_id = ?
            """,
            (artist.id, ))

        ctx.log_info(f"Deleted {cursor.rowcount} file records")

        cursor.execute(
            """
            DELETE FROM tracks
            WHERE album_id IN
            (
                SELECT id FROM albums
                WHERE artist_id = ?
            );
            """,
            (artist.id, ))

        ctx.log_info(f"Deleted {cursor.rowcount} track records")

        cursor.execute(
            """
            DELETE FROM albums
            WHERE artist_id = ?
            """,
            (artist.id, ))

        ctx.log_info(f"Deleted {cursor.rowcount} album records")

        cursor.execute(
            """
            DELETE FROM artists
            WHERE id = ?
            """,
            (artist.id, ))

        ctx.log_info(f"Deleted {cursor.rowcount} artist records")

        db.commit()


def do_delete_track(ctx):
    banner("delete track")

    with ctx.open_db() as db:
        track = select_track(db=db)
        file = File.get_by_track_id(db=db, track_id=track.id)
        show_item(track)
        show_item(file)
        confirm(ctx=ctx, prompt="Do you wish to delete this track from the database?")

        cursor = db.cursor()

        cursor.execute(
            """
            DELETE FROM tracks
            WHERE id = ?;
            """,
            (track.id, ))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to delete track ID {track.id}")

        cursor.execute(
            """
            DELETE FROM files
            WHERE id = ?;
            """,
            (file.id, ))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to delete file ID {file.id}")

        ctx.log_info(
            f"Deleted track ID {track.id} and "
            f"file ID {file.id} from database")

        db.commit()
