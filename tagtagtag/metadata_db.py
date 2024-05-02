from tagtagtag.album import Album
from tagtagtag.artist import Artist
from tagtagtag.entity import Entity
import sqlite3


class MetadataDB:
    _ENTITIES: list[Entity] = [Artist, Album]

    def __init__(self, db_path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        for entity in self.__class__._ENTITIES:
            entity.create_schema(self._conn)

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
