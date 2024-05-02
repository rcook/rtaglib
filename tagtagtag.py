from argparse import ArgumentParser
from colorama import Fore, just_fix_windows_console
from pathlib import Path
from tagtagtag.context import Context
from tagtagtag.cprint import cprint
from tagtagtag.db import do_db
from tagtagtag.dump import do_dump
from tagtagtag.error import ReportableError
from tagtagtag.ids import do_ids
from tagtagtag.scan import do_scan
import os
import sys


def default_data_dir():
    return Path(os.getenv("USERPROFILE")) / ".tagtagtag"


def main(cwd, argv, ctx):
    def path_type(s):
        return Path(cwd, s).resolve()

    parser = ArgumentParser(prog="tagtagtag", description="Tag Tool")

    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser(name="db")
    p.set_defaults(func=lambda args: do_db(ctx=ctx))

    p = subparsers.add_parser(name="dump")
    p.set_defaults(func=lambda args: do_dump(ctx=ctx, path=args.path))
    p.add_argument("path", metavar="PATH", type=path_type, help="path")

    p = subparsers.add_parser(name="ids")
    p.set_defaults(func=lambda args: do_ids(ctx=ctx, path=args.path))
    p.add_argument("path", metavar="PATH", type=path_type, help="path")

    p = subparsers.add_parser(name="scan")
    p.set_defaults(func=lambda args: do_scan(ctx=ctx, dir=args.dir))
    p.add_argument("dir", metavar="DIR", type=path_type, help="directory")

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


if __name__ == "__main__":
    just_fix_windows_console()
    main(cwd=os.getcwd(), argv=sys.argv[1:], ctx=Context())
