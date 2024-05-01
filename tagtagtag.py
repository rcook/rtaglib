from argparse import ArgumentParser
from pathlib import Path
from tagtagtag.dump import do_dump
from tagtagtag.ids import do_ids
from tagtagtag.scan import do_scan
import os
import sys


def main(cwd, argv):
    def path_type(s):
        return Path(cwd, s).resolve()

    parser = ArgumentParser(prog="tagtagtag", description="Tag Tool")

    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser(name="scan")
    p.set_defaults(func=lambda args: do_scan(dir=args.dir))
    p.add_argument("dir", metavar="DIR", type=path_type, help="directory")

    p = subparsers.add_parser(name="dump")
    p.set_defaults(func=lambda args: do_dump(path=args.path))
    p.add_argument("path", metavar="PATH", type=path_type, help="path")

    p = subparsers.add_parser(name="ids")
    p.set_defaults(func=lambda args: do_ids(path=args.path))
    p.add_argument("path", metavar="PATH", type=path_type, help="path")

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
