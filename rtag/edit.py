from rtag.track import Track
from rtag.ui import edit_item, select_artist, select_album, select_track


def do_edit(ctx, mode):
    with ctx.open_db() as db:
        while True:
            match mode:
                case "artist": result = do_edit_artist(ctx=ctx, db=db)
                case "album": result = do_edit_album(ctx=ctx, db=db)
                case "track": result = do_edit_track(ctx=ctx, db=db)
                case "album-tracks": result = do_edit_album_tracks(ctx=ctx, db=db)
                case _: raise NotImplementedError(f"Unsupported mode {mode}")
            if result is not None and not result:
                return


def do_edit_artist(ctx, db):
    artist = select_artist(db=db)

    result = edit_item(item=artist)
    if result is None or not result:
        return result

    result.update(db=db)
    ctx.log_info(f"Updated artist with ID {artist.id}")


def do_edit_album(ctx, db):
    album = select_album(db=db)
    if album is None or not album:
        return album

    result = edit_item(item=album)
    if result is None or not result:
        return result

    result.update(db=db)
    ctx.log_info(f"Updated album with ID {album.id}")


def do_edit_track(ctx, db):
    track = select_track(db=db)
    if track is None or not track:
        return track

    result = edit_item(item=track)
    if result is None or not result:
        return result

    result.update(db=db)
    ctx.log_info(f"Updated track with ID {result.id}")


def do_edit_album_tracks(ctx, db):
    album = select_album(db=db)
    if album is None or not album:
        return album

    tracks = list(
        Track.list(
            db=db,
            album_id=album.id))
    for track in tracks:
        result = edit_item(item=track)
        if result is not None and not result:
            return result

        if result is not None:
            result.update(db=db)
            ctx.log_info(f"Updated track with ID {result.id}")
