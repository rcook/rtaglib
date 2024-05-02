from colorama import Fore
from dataclasses import fields, replace
from tagtagtag.cprint import cprint


_EDIT_VALUE_PROMPT = "[Type new value, empty to leave unchanged or (Q) to quit]"


def choose_item(items, page_size):
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
                return False
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


def edit_item(item):
    def show_item(item):
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
                str(getattr(item, f.name)),
                sep="")
        print("-----")

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
            current_value,
            sep="",
            end="")

        while True:
            result = input(f" {_EDIT_VALUE_PROMPT}: ")
            if result == "Q" or result == "q":
                return False
            if result == "" or result == current_value:
                break

            try:
                new_value = f.type(result.strip())
            except ValueError:
                continue

            new_values[f.name] = new_value
            break

    if len(new_values) == 0:
        return

    return replace(item, **new_values)
