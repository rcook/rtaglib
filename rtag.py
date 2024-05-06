from argparse import ArgumentParser, BooleanOptionalAction
from colorama import Fore, just_fix_windows_console
from functools import partial
from pathlib import Path
from rtag.context import Context
from rtag.cprint import cprint
from rtag.error import ReportableError, UserCancelledError
from rtag.picard_fixup import do_picard_fixup
from rtag.fs import home_dir
from rtag._import import do_import
from rtag.retag import do_retag
from rtag.show_raw_tags import do_show_raw_tags
from rtag.show_tags import do_show_tags
import os
import rtag.delete
import rtag.edit
import rtag.merge
import rtag.show
import sys


def default_config_dir():
    return home_dir() / ".rtag"


def main(cwd, argv):
    def path_type(s):
        return Path(cwd, Path(s).expanduser()).resolve()

    def make_subparser(subparsers, *args, name, help, description=None, **kwargs):
        if description is None:
            description = help[0].upper() + help[1:]
        p = subparsers.add_parser(
            name=name,
            help=help,
            description=description)
        return p

    def add_common_args(parser):
        default = default_config_dir()
        parser.add_argument(
            "--dir",
            "-d",
            dest="config_dir",
            metavar="CONFIG_DIR",
            type=path_type,
            required=False,
            default=default,
            help=f"path to configuration directory (default: {default})")

    def add_dry_run_arg(parser):
        default = True
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action=BooleanOptionalAction,
            default=default,
            required=False,
            help=f"dry run (default: {default})")

    def add_delete_command(subparsers):
        def invoke(subcommand, ctx, args):
            func = getattr(
                rtag.delete,
                f"do_delete_{subcommand.replace('-', '_')}")
            return func(ctx=ctx)

        p = make_subparser(
            subparsers,
            name="delete",
            help="delete items from local metadata database")
        subparsers0 = p.add_subparsers(required=True, dest="subcommand")

        for subcommand in ["artist", "album", "track"]:
            p0 = make_subparser(
                subparsers0,
                name=subcommand,
                help=f"delete {subcommand} from local metadata database")
            p0.set_defaults(func=partial(invoke, subcommand))
            add_common_args(parser=p0)

    def add_edit_command(subparsers):
        def invoke(subcommand, ctx, args):
            func = getattr(
                rtag.edit,
                f"do_edit_{subcommand.replace('-', '_')}")
            return func(ctx=ctx)

        p = make_subparser(
            subparsers,
            name="edit",
            help="edit data in local metadata database")
        subparsers0 = p.add_subparsers(required=True, dest="subcommand")

        for subcommand in ["all", "artist", "album", "track", "album-tracks"]:
            p0 = make_subparser(
                subparsers0,
                name=subcommand,
                help=f"edit {subcommand} in local metadata database")
            p0.set_defaults(func=partial(invoke, subcommand))
            add_common_args(parser=p0)

    def add_import_command(subparsers):
        p = make_subparser(
            subparsers,
            name="import",
            help="import data into local metadata database")
        p.set_defaults(
            func=lambda ctx, args:
            do_import(ctx=ctx, dir=args.dir, init=args.init))
        add_common_args(parser=p)
        p.add_argument(
            "--init",
            metavar="INIT",
            action=BooleanOptionalAction,
            required=False,
            default=False,
            help="clear/initialize database from scratch (default: False)")
        p.add_argument(
            "dir",
            metavar="DIR",
            type=path_type,
            help="path to music files")

    def add_merge_command(subparsers):
        def invoke(subcommand, ctx, args):
            func = getattr(
                rtag.merge,
                f"do_merge_{subcommand.replace('-', '_')}")
            return func(ctx=ctx)

        p = make_subparser(
            subparsers,
            name="merge",
            help="merge data in local metadata database")
        subparsers0 = p.add_subparsers(required=True, dest="subcommand")

        for subcommand in ["artists", "albums"]:
            p0 = make_subparser(
                subparsers0,
                name=subcommand,
                help=f"merge {subcommand} in local metadata database")
            p0.set_defaults(func=partial(invoke, subcommand))
            add_common_args(parser=p0)

    def add_picard_fixup_command(subparsers):
        p = make_subparser(
            subparsers,
            name="picard-fixup",
            help="fix up tags post-Picard")
        p.set_defaults(func=lambda ctx, args: do_picard_fixup(ctx=ctx))
        add_common_args(parser=p)
        add_dry_run_arg(parser=p)

    def add_retag_command(subparsers):
        p = make_subparser(
            subparsers,
            name="retag",
            help="retag and move files based on local metadata database")
        p.set_defaults(
            func=lambda ctx, args:
            do_retag(ctx=ctx, dry_run=args.dry_run))
        add_common_args(parser=p)
        add_dry_run_arg(parser=p)

    def add_show_command(subparsers):
        def invoke(subcommand, ctx, args):
            func = getattr(
                rtag.show,
                f"do_show_{subcommand.replace('-', '_')}")
            return func(ctx=ctx)

        p = make_subparser(
            subparsers,
            name="show",
            help="show data from local metadata database")
        subparsers0 = p.add_subparsers(required=True, dest="subcommand")

        for subcommand in ["artist", "album", "track", "album-tracks"]:
            p0 = make_subparser(
                subparsers0,
                name=subcommand,
                help=f"edit {subcommand} in local metadata database")
            p0.set_defaults(func=partial(invoke, subcommand))
            add_common_args(parser=p0)

    def add_show_raw_tags_command(subparsers):
        p = make_subparser(
            subparsers,
            name="show-raw-tags",
            help="summarize raw tags in files")
        p.set_defaults(
            func=lambda ctx, args:
            do_show_raw_tags(ctx=ctx, path=args.path, detail=args.detail))
        default = False
        p.add_argument(
            "--detail",
            dest="detail",
            action=BooleanOptionalAction,
            required=False,
            default=default,
            help=f"show detail (default: {default})")
        p.add_argument(
            "path",
            metavar="PATH",
            type=path_type,
            help="path to directory or file")

    def add_show_tags_command(subparsers):
        p = make_subparser(
            subparsers,
            name="show-tags",
            help="show tags")
        p.set_defaults(
            func=lambda ctx, args:
            do_show_tags(ctx=ctx, dir=args.dir))
        add_common_args(parser=p)
        p.add_argument("dir", metavar="DIR", type=path_type, help="directory")

    parser = ArgumentParser(prog="rtag", description="Richard's Tagging Tool")
    subparsers = parser.add_subparsers(required=True, dest="command")
    add_delete_command(subparsers=subparsers)
    add_edit_command(subparsers=subparsers)
    add_import_command(subparsers=subparsers)
    add_merge_command(subparsers=subparsers)
    add_picard_fixup_command(subparsers=subparsers)
    add_retag_command(subparsers=subparsers)
    add_show_command(subparsers=subparsers)
    add_show_raw_tags_command(subparsers=subparsers)
    add_show_tags_command(subparsers=subparsers)

    args = parser.parse_args(argv)

    ctx = Context(args=args)
    operation = [args.command]
    if (temp := getattr(args, "subcommand", None)) is not None:
        operation.append(temp)

    try:
        with ctx.timing(operation=operation):
            status = args.func(ctx=ctx, args=args)
    except ReportableError as e:
        m = str(e)
        m = "(No message)" if len(m) == 0 else m
        cprint(Fore.LIGHTRED_EX, m, file=sys.stderr)
        sys.exit(e.exit_code)
    except UserCancelledError:
        cprint(Fore.LIGHTBLUE_EX, "Operation cancelled by user")
        sys.exit(0)

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
