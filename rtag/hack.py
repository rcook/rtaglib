from rtag.metadata.metadata import Metadata
import re


SPLIT_RE = re.compile("[/\\- ._]")


def do_hack(ctx, path):
    assert path.is_dir()

    tracks = []
    unnumbered_tracks = []

    paths = sorted(path.iterdir())
    for p in paths:
        numbers = []
        for part in SPLIT_RE.split(p.name):
            try:
                numbers.append(int(part))
            except ValueError:
                pass

        if len(numbers) == 1 and numbers[0] <= len(paths):
            tracks.append((numbers[0], p))
        else:
            unnumbered_tracks.append(p)

    offset = max(map(lambda p: p[0], tracks))
    tracks.extend((i + offset + 1, p) for i, p in enumerate(unnumbered_tracks))
    for track_number, p in tracks:
        m = Metadata.load(p)
        changed = False

        if m.track_title is None:
            changed = True
            m.track_title = p.with_suffix("").name

        if m.track_number is None:
            changed = True
            m.track_number = track_number

        if changed:
            m.save()
