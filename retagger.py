from argparse import ArgumentParser, BooleanOptionalAction
from colorama import Fore
from pathlib import Path
from retagger.cprint import cprint
from retagger.config import Config
from retagger.context import Context
from retagger.error import ReportableError
from retagger.fixup import do_fixup
from retagger.time import timing
import colorama
import os
import sys


def main(cwd, argv):
    parser = ArgumentParser(
        prog="tagger",
        description="Tag Fixer-Upper")
    subparsers = parser.add_subparsers(required=True, dest="command")

    p = subparsers.add_parser(
        name="fixup",
        description="Fix up tags post-Picard")
    p.set_defaults(
        func=lambda ctx, config,
        args: do_fixup(
            ctx=ctx,
            config=config))

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

    args = parser.parse_args(argv)

    ctx = Context.from_args(args)
    config = Config.load(args.config_path)
    with timing(args.command):
        try:
            result = args.func(ctx=ctx, config=config, args=args)
        except ReportableError as e:
            cprint(Fore.LIGHTRED_EX, e, file=sys.stderr)
            sys.exit(1)

    if result is None:
        pass
    elif isinstance(result, bool):
        if not result:
            sys.exit(1)
    elif isinstance(result, int):
        if result != 0:
            sys.exit(1)
    else:
        raise NotImplementedError(f"Unsupported return value {result}")


if __name__ == "__main__":
    colorama.just_fix_windows_console()
    main(cwd=os.getcwd(), argv=sys.argv[1:])
