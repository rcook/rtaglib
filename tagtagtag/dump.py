from tagtagtag.metadata import Metadata


def do_dump(path):
    print(f"Dumping tags for {path}")

    m = Metadata(path)
    print(m.pprint())
