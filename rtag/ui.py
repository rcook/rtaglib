from colorama import Fore
from dataclasses import fields, replace
from rtag.album import Album
from rtag.artist import Artist
from rtag.collections import DictPlus
from rtag.cprint import cprint
from rtag.error import UserCancelledError
from rtag.track import Track


_PAGE_SIZE = 20
_EMPTY_PLACEHOLDER = "(empty)"
_EDIT_VALUE_PROMPT = f"[Type new value, empty to leave unchanged, " \
    f"{_EMPTY_PLACEHOLDER} to set to NULL or (Q) to quit]"


def banner(s):
    width = len(s.upper())
    line = "-" * width
    cprint(Fore.LIGHTMAGENTA_EX, line)
    cprint(Fore.LIGHTMAGENTA_EX, s.upper())
    cprint(Fore.LIGHTMAGENTA_EX, line)


def choose_item(items, page_size, detail_func=None):
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
            if detail_func is None:
                cprint(
                    Fore.LIGHTWHITE_EX,
                    "  (",
                    Fore.LIGHTYELLOW_EX,
                    f"{i + 1}",
                    Fore.LIGHTWHITE_EX,
                    ") ",
                    Fore.LIGHTGREEN_EX,
                    item.title,
                    sep="")
            else:
                detail = detail_func(item)
                cprint(
                    Fore.LIGHTWHITE_EX,
                    "  (",
                    Fore.LIGHTYELLOW_EX,
                    f"{i + 1}",
                    Fore.LIGHTWHITE_EX,
                    ") ",
                    Fore.LIGHTGREEN_EX,
                    item.title,
                    Fore.LIGHTWHITE_EX,
                    " (",
                    Fore.LIGHTCYAN_EX,
                    detail,
                    Fore.LIGHTWHITE_EX,
                    ")",
                    sep="")

        while True:
            result = input(
                f"Choose (1)-({page_item_count}), (Enter) to go to next page, (Q) to quit: ").strip()
            if result == "Q" or result == "q":
                raise UserCancelledError()
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
    raise UserCancelledError()


def select_artist(db, **kwargs):
    return choose_item(
        items=list(Artist.list(db=db)),
        page_size=_PAGE_SIZE,
        **kwargs)


def select_album(db, **kwargs):
    artist = select_artist(db=db)
    return choose_item(
        items=list(Album.list(db=db, artist_id=artist.id)),
        page_size=_PAGE_SIZE,
        **kwargs)


def select_track(db, **kwargs):
    album = select_album(db=db)
    return choose_item(
        items=list(Track.list(db=db, album_id=album.id)),
        page_size=_PAGE_SIZE,
        **kwargs)


def show_item(item):
    def pretty(name):
        value = getattr(item, name)
        return "(empty)" if value is None else str(value)

    name_width = 0
    for f in fields(item):
        name_width = max(name_width, len(f.name))

    cprint(Fore.LIGHTCYAN_EX, item.__class__.__name__)
    for f in fields(item):
        cprint(
            Fore.LIGHTYELLOW_EX,
            "  ",
            f.name.ljust(name_width),
            Fore.LIGHTWHITE_EX,
            " : ",
            Fore.LIGHTGREEN_EX,
            pretty(f.name),
            sep="")
    print("-----")


def edit_item(item):
    show_item(item=item)

    fixed_fields = {"id", "uuid"}
    editable_fields = list(
        filter(
            lambda x:
            x.name not in fixed_fields and not x.name.endswith("_id"),
            fields(item)))

    new_values = {}
    for f in editable_fields:
        current_value = getattr(item, f.name)
        cprint(
            Fore.LIGHTYELLOW_EX,
            f.name,
            " = ",
            Fore.LIGHTGREEN_EX,
            "(empty)" if current_value is None else current_value,
            sep="",
            end="")

        while True:
            result = input(f" {_EDIT_VALUE_PROMPT}: ").strip()
            if result == "Q" or result == "q":
                raise UserCancelledError()
            if result == "" or result != _EMPTY_PLACEHOLDER and result == current_value:
                break

            if result == _EMPTY_PLACEHOLDER:
                new_value = None
            else:
                try:
                    new_value = f.type(result)
                except ValueError:
                    continue

            new_values[f.name] = new_value
            break

    if len(new_values) == 0:
        return

    return replace(item, **new_values)


def confirm(ctx, prompt):
    result = input(f"{prompt} [YES/N]: ")
    if result != "YES":
        ctx.log_info("Operation cancelled")
        raise UserCancelledError()

    ctx.log_info("Operation confirmed")


def select_artists(db):
    selection = []

    while True:
        artist = select_artist(db=db)
        selection.append(artist)

        cprint(Fore.LIGHTCYAN_EX, "Selected artist(s):")
        for artist in selection:
            cprint(
                Fore.LIGHTGREEN_EX,
                "  ",
                artist.title,
                sep="")

        if len(selection) > 1:
            while True:
                result = input(
                    "[Press Enter to add more artists, press (M) to merge these artists or (Q) to quit] ").strip()
                if result == "Q" or result == "q":
                    raise UserCancelledError()
                if result == "":
                    break
                if result == "M" or result == "m":
                    return selection


def select_albums(db):
    artists = DictPlus()

    def get_detail(item):
        artist = artists.get_or_add(
            item.artist_id,
            lambda artist_id: Artist.get_by_id(db=db, id=artist_id))
        return artist.title

    selection = []

    while True:
        album = select_album(db=db, detail_func=get_detail)
        selection.append(album)

        cprint(Fore.LIGHTCYAN_EX, "Selected album(s):")
        for album in selection:
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

        if len(selection) > 1:
            while True:
                result = input(
                    "[Press Enter to add more albums, press (M) to merge these albums or (Q) to quit] ").strip()
                if result == "Q" or result == "q":
                    raise UserCancelledError()
                if result == "":
                    break
                if result == "M" or result == "m":
                    return selection
