from argparse import ArgumentParser
from copy import deepcopy
from mutagen.easyid3 import EasyID3
from pathlib import Path
from uuid import UUID, uuid4
import mutagen
import mutagen.id3
import os
import sys


MISSING_ARG = object()
ALBUM_ID_KEY = "rcook_album_id"
TRACK_ID_KEY = "rcook_track_id"
KEYS = [
    (ALBUM_ID_KEY, "RCOOK_ALBUM_ID"),
    (TRACK_ID_KEY, "RCOOK_TRACK_ID"),
]


class Metadata:
    class Accessor:
        def __init__(self, metadata, key):
            self._metadata = metadata
            self._key = key

        def get(self, default=MISSING_ARG):
            return self._metadata.get(key=self._key, default=default)

        def set(self, value):
            self._metadata.set(key=self._key, value=value)

        def pop(self, default=MISSING_ARG):
            self._metadata.pop(key=self._key, default=default)

    def __init__(self, path):
        self._path = path
        self._m = mutagen.File(self._path, easy=True)
        self._saved_tags = {} \
            if self._m.tags is None \
            else deepcopy(self._m.tags.__dict__)
        self.album_id = Metadata.Accessor(self, ALBUM_ID_KEY)
        self.track_id = Metadata.Accessor(self, TRACK_ID_KEY)

    @property
    def dirty(self):
        d = {} if self._m.tags is None else self._m.tags.__dict__
        return d != self._saved_tags

    def save(self):
        if self.dirty:
            if len(self._m.tags) == 0:
                self._m.delete()
            else:
                self._m.save()
        self._m = None

    def delete(self):
        self._m.delete()
        self._m = None

    def get(self, key, default=MISSING_ARG):
        if default is MISSING_ARG:
            if self._m.tags is None:
                raise KeyError(key)
        else:
            if self._m.tags is None or key not in self._m.tags:
                return default
        value = self._m.tags[key]
        assert isinstance(value, list) and len(value) == 1
        return value[0]

    def set(self, key, value):
        if self._m.tags is None:
            self._m.add_tags()
        self._m.tags[key] = value

    def pop(self, key, default=MISSING_ARG):
        if default is MISSING_ARG:
            if self._m.tags is None:
                raise KeyError(key)
            return self._m.tags.pop(key)
        else:
            if self._m.tags is None:
                return default
            return self._m.tags.pop(key, default)


def main(cwd, argv):
    def path_type(s):
        return Path(cwd, s).resolve()

    parser = ArgumentParser(prog="tagtagtag", description="Tag Tool")
    parser.add_argument("path", type=path_type, help="Path")

    args = parser.parse_args(argv)

    status = run(path=args.path)
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


def run(path):
    m = Metadata(path)

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


if __name__ == "__main__":
    for key, id in KEYS:
        EasyID3.RegisterTXXXKey(key, id)
    main(cwd=os.getcwd(), argv=sys.argv[1:])
