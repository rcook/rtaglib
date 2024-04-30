from copy import deepcopy
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4Tags
import mutagen
import mutagen.id3


MISSING_ARG = object()


class Metadata:
    ALBUM_ID_KEY = "rcook_album_id"
    TRACK_ID_KEY = "rcook_track_id"
    KEYS = [
        (ALBUM_ID_KEY, "RCOOK_ALBUM_ID"),
        (TRACK_ID_KEY, "RCOOK_TRACK_ID"),
    ]
    _first_instance = True

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
        if self.__class__._first_instance:
            self.__class__._first_instance = False
            for key, id in self.__class__.KEYS:
                EasyID3.RegisterTXXXKey(key, id)
                EasyMP4Tags.RegisterFreeformKey(key, id, mean="org.rcook")

        self._path = path
        self._m = mutagen.File(self._path, easy=True)
        self._saved_tags = {} \
            if self._m.tags is None \
            else deepcopy(self._m.tags.__dict__)
        self.album_id = self.__class__.Accessor(
            self,
            self.__class__.ALBUM_ID_KEY)
        self.track_id = self.__class__.Accessor(
            self,
            self.__class__.TRACK_ID_KEY)

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

    def pprint(self):
        return self._m.pprint()

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
