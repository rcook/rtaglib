from argparse import ArgumentParser
from pathlib import Path
from tagtagtag.ids import do_ids
import os
import sys


def main(cwd, argv):
    def path_type(s):
        return Path(cwd, s).resolve()

    parser = ArgumentParser(prog="tagtagtag", description="Tag Tool")

    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser(name="ids")
    p.set_defaults(func=lambda args: do_ids(path=args.path))
    p.add_argument("path", type=path_type, help="Path")

    args = parser.parse_args(argv)

    status = args.func(args=args)
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
    main(cwd=os.getcwd(), argv=sys.argv[1:])
