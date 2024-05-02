from colorama import Fore
from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.cprint import cprint
from tagtagtag.metadata_db import MetadataDB
from tagtagtag.track import Track


_PAGE_SIZE = 5


def do_edit(ctx, data_dir):
    db_path = data_dir / "metadata.db"

    with MetadataDB(db_path) as db:
        artist = choose(
            items=list(Artist.list(db=db)),
            page_size=_PAGE_SIZE)
        if artist is None:
            return

        album = choose(
            items=list(
                Album.list(
                    db=db,
                    artist_id=artist.id)),
            page_size=_PAGE_SIZE)
        if album is None:
            return

        track = choose(
            items=list(
                Track.list(
                    db=db,
                    album_id=album.id)),
            page_size=_PAGE_SIZE)
        if track is None:
            return

        print(artist)
        print(album)
        print(track)


def choose(items, page_size):
    item_count = len(items)
    page_count = item_count // page_size
    if item_count % page_size > 0:
        page_count += 1

    page_number = 0
    while page_number < page_count:
        cprint(
            Fore.LIGHTCYAN_EX,
            f"Page {page_number + 1} of {page_count} "
            f"(total: {item_count})")

        index = page_number * page_size
        page_items = items[index:index + page_size]
        page_item_count = len(page_items)
        for i, item in enumerate(page_items):
            cprint(
                Fore.LIGHTWHITE_EX,
                "  (",
                Fore.LIGHTYELLOW_EX,
                f"{i + 1}",
                Fore.LIGHTWHITE_EX,
                ") ",
                Fore.LIGHTGREEN_EX,
                item.name,
                sep="")

        while True:
            result = input(
                f"Choose (1)-({page_item_count}), (Enter) to go to next page, (Q) to quit: ").lower()

            if result == "q":
                return
            if result == "":
                page_number += 1
                break

            try:
                choice = int(result)
            except ValueError:
                continue

            if choice < 1 or choice > page_item_count:
                continue

            item = page_items[choice - 1]
            return item
