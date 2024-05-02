from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.metadata_db import MetadataDB
from tagtagtag.track import Track
from tagtagtag.ui import choose_item, edit_item


_PAGE_SIZE = 5


def do_edit(ctx, data_dir, mode):
    db_path = data_dir / "metadata.db"
    with MetadataDB(db_path) as db:
        while True:
            match mode:
                case "artist": result = do_edit_artist(ctx=ctx, db=db)
                case "album": result = do_edit_album(ctx=ctx, db=db)
                case "track": result = do_edit_track(ctx=ctx, db=db)
                case _: raise NotImplementedError(f"Unsupported mode {mode}")
            if result is not None and not result:
                return


def do_edit_artist(ctx, db):
    pass


def do_edit_album(ctx, db):
    pass


def do_edit_track(ctx, db):
    artist = choose_item(
        items=list(Artist.list(db=db)),
        page_size=_PAGE_SIZE)
    if artist is None or not artist:
        return artist

    album = choose_item(
        items=list(
            Album.list(
                db=db,
                artist_id=artist.id)),
        page_size=_PAGE_SIZE)
    if album is None or not album:
        return album

    track = choose_item(
        items=list(
            Track.list(
                db=db,
                album_id=album.id)),
        page_size=_PAGE_SIZE)
    if track is None or not track:
        return track

    result = edit_item(item=track)
    if result is None or not result:
        return result

    result.update(db=db)
    ctx.log_info(f"Updated track with ID {result.id}")
