from rtag.file import File
from rtag.ui import banner, confirm, select_track, show_item


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
