from colorama import Fore
from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.collections import DictPlus
from tagtagtag.cprint import cprint
from tagtagtag.metadata_db import MetadataDB
from tagtagtag.ui import choose_item, edit_item


_PAGE_SIZE = 20


def do_merge(ctx, data_dir, mode):
    db_path = data_dir / "metadata.db"
    with MetadataDB(db_path) as db:
        match mode:
            case "artists": result = do_merge_artists(ctx=ctx, db=db)
            case "albums": result = do_merge_albums(ctx=ctx, db=db)
            case _: raise NotImplementedError(f"Unsupported mode {mode}")


def do_merge_artists(ctx, db):
    artist = choose_item(
        items=list(Artist.list(db=db)),
        page_size=_PAGE_SIZE)
    if artist is None or not artist:
        return artist

    result = edit_item(item=artist)
    if result is None or not result:
        return result

    result.update(db=db)
    ctx.log_info(f"Updated artist with ID {artist.id}")


def do_merge_albums(ctx, db):
    artists = DictPlus()

    def get_detail(item):
        artist = artists.get_or_add(
            item.artist_id,
            lambda artist_id: Artist.get_by_id(db=db, id=artist_id))
        return artist.title

    selected_albums = []

    while True:
        album = choose_item(
            items=list(Album.list_all(db=db)),
            page_size=_PAGE_SIZE,
            detail_func=get_detail)
        if album is not None and not album:
            return False

        selected_albums.append(album)

        cprint(Fore.LIGHTCYAN_EX, "Selected album(s):")
        for album in selected_albums:
            cprint(
                Fore.LIGHTGREEN_EX,
                "  ",
                album.title,
                Fore.LIGHTWHITE_EX,
                " (",
                Fore.LIGHTCYAN_EX,
                artists[album.artist_id].title,
                Fore.LIGHTWHITE_EX,
                ")",
                sep="")

        if len(selected_albums) > 1:
            while True:
                result = input(
                    "[Press Enter to add more albums, press (M) to merge these albums or (Q) to quit] ").strip()
                if result == "Q" or result == "q":
                    return False
                if result == "":
                    break
                if result == "M" or result == "m":
                    break
            if result == "M" or result == "m":
                break

    album, *other_albums = selected_albums

    album_ids = tuple(x.id for x in selected_albums)
    placeholders = ", ".join("?" * len(other_albums))

    cursor = db.cursor()

    cursor.execute(
        f"""
        UPDATE tracks
        SET album_id = ?
        WHERE album_id IN ({placeholders})
        """,
        album_ids)
    ctx.log_info(
        f"Merged albums {', '.join(str(x) for x in album_ids)} "
        f"({cursor.rowcount} tracks updated)")

    cursor.execute(
        f"""
        DELETE FROM albums WHERE id IN ({placeholders})
        """,
        tuple(x.id for x in other_albums))
    ctx.log_info(f"Delete merged albums ({cursor.rowcount} albums deleted)")

    db.commit()
