from rtag.metadata.metadata import Metadata
from rtag.ui import select_albums, select_artists


def do_merge_artists(ctx):
    with ctx.open_db() as db:
        artist, *other_artists = select_artists(db=db)
        other_artist_ids = [x.id for x in other_artists]
        all_artist_ids = [artist.id] + other_artist_ids
        other_placeholders = ", ".join("?" * len(other_artists))

        cursor = db.cursor()

        cursor.execute(
            f"""
            UPDATE albums
            SET artist_id = ?
            WHERE artist_id IN ({other_placeholders})
            """,
            all_artist_ids)
        ctx.log_info(
            f"Merged albums {', '.join(str(x) for x in all_artist_ids)} "
            f"({cursor.rowcount} albums updated)")

        cursor.execute(
            f"""
            DELETE FROM artists WHERE id IN ({other_placeholders})
            """,
            other_artist_ids)
        ctx.log_info(f"Delete merged artists ({
                     cursor.rowcount} artists deleted)")

        cursor.execute(
            f"""
            SELECT path
            FROM files
            WHERE artist_id IN ({other_placeholders})
            """,
            other_artist_ids)
        for path, in cursor.fetchall():
            m = Metadata.load(path)
            m.rcook_artist_id = artist.uuid
            m.save()
        ctx.log_info(f"Updated tags in associated files")

        db.commit()


def do_merge_albums(ctx):
    with ctx.open_db() as db:
        album, *other_albums = select_albums(db=db)
        other_album_ids = [x.id for x in other_albums]
        all_album_ids = [album.id] + other_album_ids
        other_placeholders = ", ".join("?" * len(other_albums))

        cursor = db.cursor()

        cursor.execute(
            f"""
            UPDATE tracks
            SET album_id = ?
            WHERE album_id IN ({other_placeholders})
            """,
            all_album_ids)
        ctx.log_info(
            f"Merged albums {', '.join(str(x) for x in all_album_ids)} "
            f"({cursor.rowcount} tracks updated)")

        cursor.execute(
            f"""
            DELETE FROM albums WHERE id IN ({other_placeholders})
            """,
            other_album_ids)
        ctx.log_info(
            f"Delete merged albums ({cursor.rowcount} "
            "albums deleted)")

        cursor.execute(
            f"""
            SELECT path
            FROM files
            WHERE album_id IN ({other_placeholders})
            """,
            other_album_ids)
        for path, in cursor.fetchall():
            m = Metadata.load(path)
            m.rcook_album_id = album.uuid
            m.save()
        ctx.log_info(f"Updated tags in associated files")

        db.commit()
