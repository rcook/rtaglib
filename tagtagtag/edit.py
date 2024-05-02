from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.metadata_db import MetadataDB
from tagtagtag.track import Track
from tagtagtag.ui import choose_item, edit_item


_PAGE_SIZE = 5


def do_edit(ctx, data_dir):
    db_path = data_dir / "metadata.db"

    with MetadataDB(db_path) as db:
        """
        artist = choose_item(
            items=list(Artist.list(db=db)),
            page_size=_PAGE_SIZE)
        if artist is None:
            return

        album = choose_item(
            items=list(
                Album.list(
                    db=db,
                    artist_id=artist.id)),
            page_size=_PAGE_SIZE)
        if album is None:
            return

        track = choose_item(
            items=list(
                Track.list(
                    db=db,
                    album_id=album.id)),
            page_size=_PAGE_SIZE)
        if track is None:
            return

        edit_item(item=track)
        """

        result = edit_item(item=Track.get_by_id(db=db, id=1))
        if result is not None:
            if not result:
                return
            result.update(db=db)
            ctx.log_info(f"Updated track with ID {result.id}")
