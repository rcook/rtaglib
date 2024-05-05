from colorama import Fore
from rtag.artist import Artist
from rtag.cprint import cprint
from rtag.track import Track
from rtag.ui import select_album, select_artist, select_track, show_item


def do_show_artist(ctx):
    with ctx.open_db() as db:
        show_item(select_artist(db=db))


def do_show_album(ctx):
    with ctx.open_db() as db:
        show_item(select_album(db=db))


def do_show_track(ctx):
    with ctx.open_db() as db:
        show_item(select_track(db=db))


def do_show_album_tracks(ctx):
    with ctx.open_db() as db:
        album = select_album(db=db)
        artist = Artist.get_by_id(db=db, id=album.artist_id)
        cprint(Fore.LIGHTCYAN_EX, f"{artist.title}: {album.title}")

        tracks = list(Track.list(db=db, album_id=album.id))
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
