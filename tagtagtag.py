from argparse import ArgumentParser, BooleanOptionalAction
from colorama import Fore, just_fix_windows_console
from pathlib import Path
from tagtagtag.context import Context
from tagtagtag.cprint import cprint
from tagtagtag.dump import do_dump
from tagtagtag.edit import do_edit
from tagtagtag.error import ReportableError
from tagtagtag.fs import home_dir
from tagtagtag.ids import do_ids
from tagtagtag._import import do_import
from tagtagtag.merge import do_merge
from tagtagtag.scan import do_scan
from tagtagtag.show import do_show
import os
import sys


def default_data_dir():
    return home_dir() / ".tagtagtag"


def main(cwd, argv, ctx):
    def path_type(s):
        return Path(cwd, s).resolve()

    def add_common_args(parser):
        default = default_data_dir()
        parser.add_argument(
            "--dir",
            "-d",
            dest="data_dir",
            metavar="DATA_DIR",
            type=path_type,
            required=False,
            default=default,
            help=f"path to data directory (default: {default})")

    parser = ArgumentParser(prog="tagtagtag", description="Tag Tool")

    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser(name="edit")
    p.set_defaults(
        func=lambda args: do_edit(
            ctx=ctx,
            data_dir=args.data_dir,
            mode=args.mode))
    add_common_args(parser=p)
    p.add_argument(
        "mode",
        choices=["artist", "album", "track", "album-tracks"],
        help="edit artist, album or track")

    p = subparsers.add_parser(name="import")
    p.set_defaults(
        func=lambda args: do_import(
            ctx=ctx,
            data_dir=args.data_dir,
            music_dir=args.music_dir,
            init=args.init,
            new_ids=args.new_ids))
    add_common_args(parser=p)
    p.add_argument(
        "--init",
        metavar="INIT",
        action=BooleanOptionalAction,
        required=False,
        default=False,
        help="clear/initialize database from scratch (default: False)")
    p.add_argument(
        "--new-ids",
        metavar="NEW_IDS",
        action=BooleanOptionalAction,
        required=False,
        default=False,
        help="force generation of new RCOOK_xxx IDs (default: False)")
    p.add_argument(
        "music_dir",
        metavar="MUSIC_DIR",
        type=path_type,
        help="path to music files")

    p = subparsers.add_parser(name="dump")
    p.set_defaults(func=lambda args: do_dump(ctx=ctx, path=args.path))
    p.add_argument("path", metavar="PATH", type=path_type, help="path")

    p = subparsers.add_parser(name="ids")
    p.set_defaults(func=lambda args: do_ids(ctx=ctx, path=args.path))
    p.add_argument("path", metavar="PATH", type=path_type, help="path")

    p = subparsers.add_parser(name="merge")
    p.set_defaults(
        func=lambda args: do_merge(
            ctx=ctx,
            data_dir=args.data_dir,
            mode=args.mode))
    add_common_args(parser=p)
    p.add_argument(
        "mode",
        choices=["artists", "albums"],
        help="merge artists or albums")

    p = subparsers.add_parser(name="scan")
    p.set_defaults(func=lambda args: do_scan(ctx=ctx, dir=args.dir))
    p.add_argument("dir", metavar="DIR", type=path_type, help="directory")

    p = subparsers.add_parser(name="show")
    p.set_defaults(
        func=lambda args: do_show(
            ctx=ctx,
            data_dir=args.data_dir,
            mode=args.mode))
    add_common_args(parser=p)
    p.add_argument(
        "mode",
        choices=["album-tracks"],
        help="show artist, album or track")

    args = parser.parse_args(argv)

    try:
        status = args.func(args=args)
    except ReportableError as e:
        m = str(e)
        m = "(No message)" if len(m) == 0 else m
        cprint(Fore.LIGHTRED_EX, m, file=sys.stderr)
        sys.exit(e.exit_code)

    if status is None:
        pass
    elif isinstance(status, bool):
        if not status:
            sys.exit(1)
    elif isinstance(status, int):
        if status != 0:
            sys.exit(status)
    else:
        raise NotImplementedError(f"Unsupported status {status}")


def test():
    from tagtagtag.new_metadata import Metadata
    from uuid import uuid4

    m = Metadata.load(
        "C:\\Users\\rcook\\Desktop\\Beets\\samples.bak\\Pink_Floyd\\Dark_Side_of_the_Moon\\sample1.flac")

    for tag in m.tags:
        print(f"{tag} = {m.get_tag(tag, default=None)}")


if __name__ == "__main__":
    just_fix_windows_console()
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        test()
    else:
        main(cwd=os.getcwd(), argv=sys.argv[1:], ctx=Context())
