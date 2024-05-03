from rtag.metadata import Metadata
from uuid import UUID, uuid4


def do_ids(ctx, path):
    print(f"Adding track and album IDs to {path}")
    m = Metadata.load(path)

    current_album_id = None \
        if (temp := m.album_id.get(None)) is None \
        else UUID(temp)
    if current_album_id is None:
        m.album_id.set(str(uuid4()))
    else:
        print(f"Album ID: {current_album_id}")

    current_track_id = None \
        if (temp := m.track_id.get(None)) is None \
        else UUID(temp)
    if current_track_id is None:
        m.track_id.set(str(uuid4()))
    else:
        print(f"Track ID: {current_track_id}")

    if m.dirty:
        print("Saving changes")
        m.save()
    else:
        print("No changes")
