from argparse import ArgumentParser, BooleanOptionalAction
from colorama import Fore, just_fix_windows_console
from pathlib import Path
from rtag.context import Context
from rtag.cprint import cprint
from rtag.dump import do_dump
from rtag.edit import do_edit
from rtag.error import ReportableError
from rtag.picard_fixup import do_picard_fixup
from rtag.fs import home_dir
from rtag.ids import do_ids
from rtag._import import do_import
from rtag.list_dir import do_list_dir
from rtag.merge import do_merge
from rtag.scan import do_scan
from rtag.show import do_show
import os
import sys


def default_data_dir():
    return home_dir() / ".rtag"


def main(cwd, argv):
    def path_type(s):
        return Path(cwd, s).resolve()

    def make_subparser(subparsers, *args, name, help, description=None, **kwargs):
        if description is None:
            description = help[0].upper() + help[1:]
        p = subparsers.add_parser(
            name=name,
            help=help,
            description=description)
        return p

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

    def add_dump_command(subparsers):
        p = make_subparser(
            subparsers,
            name="dump",
            help="dump out tags for file")
        p.set_defaults(func=lambda ctx, args: do_dump(ctx=ctx, path=args.path))
        p.add_argument("path", metavar="PATH", type=path_type, help="path")

    def add_edit_command(subparsers):
        p = make_subparser(
            subparsers,
            name="edit",
            help="edit data in local metadata database")
        p.set_defaults(
            func=lambda ctx, args:
            do_edit(
                ctx=ctx,
                data_dir=args.data_dir,
                mode=args.mode))
        add_common_args(parser=p)
        p.add_argument(
            "mode",
            choices=["artist", "album", "track", "album-tracks"],
            help="edit artist, album or track")

    def add_import_command(subparsers):
        p = make_subparser(
            subparsers,
            name="import",
            help="import data into local metadata database")
        p.set_defaults(
            func=lambda ctx, args:
            do_import(
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

    def add_ids_command(subparsers):
        p = make_subparser(
            subparsers,
            name="ids",
            help="add IDs to file")
        p.set_defaults(func=lambda ctx, args: do_ids(ctx=ctx, path=args.path))
        p.add_argument("path", metavar="PATH", type=path_type, help="path")

    def add_list_dir_command(subparsers):
        p = make_subparser(
            subparsers,
            name="list-dir",
            help="list contents of directory")
        p.set_defaults(
            func=lambda ctx, args:
            do_list_dir(
                ctx=ctx,
                dir=args.dir))
        p.add_argument("dir", metavar="DIR", type=path_type, help="directory")

    def add_merge_command(subparsers):
        p = make_subparser(
            subparsers,
            name="merge",
            help="merge artists or albums in local metadata database")
        p.set_defaults(
            func=lambda ctx, args:
            do_merge(
                ctx=ctx,
                data_dir=args.data_dir,
                mode=args.mode))
        add_common_args(parser=p)
        p.add_argument(
            "mode",
            choices=["artists", "albums"],
            help="merge artists or albums")

    def add_picard_fixup_command(subparsers):
        p = make_subparser(
            subparsers,
            name="picard-fixup",
            help="fix up tags post-Picard")
        p.set_defaults(func=lambda ctx, args: do_picard_fixup(ctx=ctx))

        default = Path(cwd, "config.yaml")
        if default.is_file():
            p.add_argument(
                "--config",
                "-c",
                dest="config_path",
                type=Path,
                default=default,
                required=False,
                help=f"path to configuration file (default: {default})")
        else:
            p.add_argument(
                "--config",
                "-c",
                dest="config_path",
                type=Path,
                required=True,
                help="path to configuration file")

        p.add_argument(
            "--dry-run",
            dest="dry_run",
            action=BooleanOptionalAction,
            default=True,
            required=False,
            help="dry run (default: True)")

    def add_scan_command(subparsers):
        p = make_subparser(
            subparsers,
            name="scan",
            help="list files not in local metadata database")
        p.set_defaults(func=lambda ctx, args: do_scan(ctx=ctx, dir=args.dir))
        p.add_argument("dir", metavar="DIR", type=path_type, help="directory")

    def add_show_command(subparsers):
        p = make_subparser(
            subparsers,
            name="show",
            help="show data from local metadata database")
        p.set_defaults(
            func=lambda ctx, args:
            do_show(
                ctx=ctx,
                data_dir=args.data_dir,
                mode=args.mode))
        add_common_args(parser=p)
        p.add_argument(
            "mode",
            choices=["album-tracks"],
            help="show artist, album or track")

    parser = ArgumentParser(prog="rtag", description="Richard's Tagging Tool")
    subparsers = parser.add_subparsers(required=True, dest="command")
    add_dump_command(subparsers=subparsers)
    add_edit_command(subparsers=subparsers)
    add_import_command(subparsers=subparsers)
    add_ids_command(subparsers=subparsers)
    add_list_dir_command(subparsers=subparsers)
    add_merge_command(subparsers=subparsers)
    add_picard_fixup_command(subparsers=subparsers)
    add_scan_command(subparsers=subparsers)
    add_show_command(subparsers=subparsers)

    args = parser.parse_args(argv)

    ctx = Context(args=args)
    with ctx.timing(operation=args.command):
        try:
            status = args.func(ctx=ctx, args=args)
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


if __name__ == "__main__":
    just_fix_windows_console()
    main(cwd=os.getcwd(), argv=sys.argv[1:])
