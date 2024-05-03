from colorama import Fore
from rtag.album import Album
from rtag.artist import Artist
from rtag.cprint import cprint
from rtag.metadata_db import MetadataDB
from rtag.track import Track
from rtag.ui import choose_item


_PAGE_SIZE = 20


def do_show(ctx, data_dir, mode):
    db_path = data_dir / "metadata.db"
    with MetadataDB(db_path) as db:
        while True:
            match mode:
                case "album-tracks": result = do_show_album_tracks(ctx=ctx, db=db)
                case _: raise NotImplementedError(f"Unsupported mode {mode}")
            if result is not None and not result:
                return


def do_show_album_tracks(ctx, db):
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

    cprint(Fore.LIGHTCYAN_EX, f"{artist.title}: {album.title}")
    tracks = list(
        Track.list(
            db=db,
            album_id=album.id))
    for i, track in enumerate(tracks):
        cprint(
            Fore.LIGHTWHITE_EX,
            "  (",
            Fore.LIGHTYELLOW_EX,
            f"{i + 1}".rjust(3),
            Fore.LIGHTWHITE_EX,
            ") ",
            Fore.LIGHTGREEN_EX,
            track.title,
            Fore.LIGHTWHITE_EX,
            " [",
            Fore.LIGHTCYAN_EX,
            track.safe_title,
            Fore.LIGHTWHITE_EX,
            "]",
            ""
            if track.number == i + 1
            else Fore.LIGHTRED_EX + f" invalid track number: {track.number}",
            sep="")

    return False
