from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.metadata_db import MetadataDB


def do_db(ctx, data_dir):
    db_path = data_dir / "metadata.db"
    ctx.log_debug("do_db begin")
    ctx.log_debug(f"db_path={db_path}")

    with MetadataDB(db_path) as db:
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

    ctx.log_debug("do_db end")
