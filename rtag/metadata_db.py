from rtag.album import Album
from rtag.artist import Artist
from rtag.entity import Entity
from rtag.file import File
from rtag.track import Track
import sqlite3


class MetadataDB:
    _ENTITIES: list[Entity] = [Artist, Album, Track, File]

    def __init__(self, db_path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        for entity in self.__class__._ENTITIES:
            entity.create_schema(self._conn)

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
