from rtag.track import Track
from rtag.ui import banner, edit_item, select_artist, select_album, select_track


def do_edit_artist(ctx):
    banner("edit artist")

    with ctx.open_db() as db:
        artist = select_artist(db=db)

        result = edit_item(item=artist)
        if result is None or not result:
            return result

        result.update(db=db)
        ctx.log_info(f"Updated artist with ID {artist.id}")


def do_edit_album(ctx):
    banner("edit album")

    with ctx.open_db() as db:
        album = select_album(db=db)
        if album is None or not album:
            return album

        result = edit_item(item=album)
        if result is None or not result:
            return result

        result.update(db=db)
        ctx.log_info(f"Updated album with ID {album.id}")


def do_edit_track(ctx):
    banner("edit track")

    with ctx.open_db() as db:
        track = select_track(db=db)
        if track is None or not track:
            return track

        result = edit_item(item=track)
        if result is None or not result:
            return result

        result.update(db=db)
        ctx.log_info(f"Updated track with ID {result.id}")


def do_edit_album_tracks(ctx):
    banner("edit album tracks")

    with ctx.open_db() as db:
        album = select_album(db=db)
        if album is None or not album:
            return album

        tracks = list(Track.list(db=db, album_id=album.id))
        for track in tracks:
            result = edit_item(item=track)
            if result is not None and not result:
                return result

            if result is not None:
                result.update(db=db)
                ctx.log_info(f"Updated track with ID {result.id}")
