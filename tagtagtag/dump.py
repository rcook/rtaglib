from tagtagtag.metadata import Metadata


def do_dump(ctx, path):
    print(f"Dumping tags for {path}")
    for line in Metadata.load(path).pprint().splitlines():
        print(f"  {line}")
