from colorama import Fore
from rpycli.prelude import *
from rtag.album import Album
from rtag.artist import Artist
from rtag.track import Track
from rtag.ui import banner, edit_item, select_artist, select_album, select_track


def do_edit_artist(ctx):
    banner("edit artist")

    with ctx.open_db() as db:
        artist = select_artist(db=db)

        result = edit_item(item=artist)
        if result is None:
            return

        result.update(db=db)
        ctx.log_info(f"Updated artist with ID {artist.id}")


def do_edit_album(ctx):
    banner("edit album")

    with ctx.open_db() as db:
        album = select_album(db=db)

        result = edit_item(item=album)
        if result is None:
            return

        result.update(db=db)
        ctx.log_info(f"Updated album with ID {album.id}")


def do_edit_track(ctx):
    banner("edit track")

    with ctx.open_db() as db:
        track = select_track(db=db)

        result = edit_item(item=track)
        if result is None:
            return

        result.update(db=db)
        ctx.log_info(f"Updated track with ID {result.id}")


def do_edit_album_tracks(ctx):
    banner("edit album tracks")

    with ctx.open_db() as db:
        album = select_album(db=db)

        tracks = list(Track.list(db=db, album_id=album.id))
        for track in tracks:
            result = edit_item(item=track)
            if result is not None:
                result.update(db=db)
                ctx.log_info(f"Updated track with ID {result.id}")


def do_edit_all(ctx):
    banner("edit everything")

    with ctx.open_db() as db:
        cprint(Fore.LIGHTCYAN_EX, "Select starting artist")
        starting_artist = select_artist(db=db)

        editing = False
        for artist in Artist.list(db=db):
            if not editing and artist != starting_artist:
                continue
            editing = True

            artist0 = edit_item(item=artist)
            if artist0 is not None:
                artist0.update(db=db)
                ctx.log_info(f"Updated artist with ID {artist0.id}")

            for album in Album.list(db=db, artist_id=artist.id):
                album0 = edit_item(item=album)
                if album0 is not None:
                    album0.update(db=db)
                    ctx.log_info(f"Updated album with ID {album0.id}")

                for track in Track.list(db=db, album_id=album.id):
                    track0 = edit_item(item=track)
                    if track0 is not None:
                        track0.update(db=db)
                        ctx.log_info(f"Updated track with ID {track0.id}")
