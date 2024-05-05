from dataclasses import dataclass
from pathlib import Path
from rtag.entity import Entity
from rtag.error import ReportableError
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class File(Entity):
    id: int
    path: Path
    rel_path: Path
    artist_id: int
    album_id: int
    track_id: int

    @staticmethod
    def create_schema(db):
        db.executescript(
            """
            BEGIN;
            CREATE TABLE IF NOT EXISTS files
            (
                id INTEGER PRIMARY KEY NOT NULL,
                path TEXT NOT NULL UNIQUE,
                rel_path TEXT NOT NULL,
                artist_id INTEGER NOT NULL,
                album_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                UNIQUE(artist_id, album_id, track_id)
                FOREIGN KEY(album_id) REFERENCES albums(id)
            );
            CREATE INDEX IF NOT EXISTS files_path_idx ON files(path);
            CREATE INDEX IF NOT EXISTS files_artist_id_idx ON files(artist_id);
            CREATE INDEX IF NOT EXISTS files_album_id_idx ON files(album_id);
            CREATE INDEX IF NOT EXISTS files_track_id_idx ON files(track_id);
            COMMIT;
            """)

    @classmethod
    def list(cls, db):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, path, rel_path, artist_id, album_id, track_id FROM files ORDER BY path")
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                path=Path(row[1]),
                rel_path=Path(row[2]),
                artist_id=row[3],
                album_id=row[4],
                track_id=row[5])

    @classmethod
    def create(cls, db, path, rel_path, artist_id, album_id, track_id):
        file = cls.try_create(
            db=db,
            path=path,
            rel_path=rel_path,
            artist_id=artist_id,
            album_id=album_id,
            track_id=track_id)
        if file is not None:
            return file

        raise ReportableError(f"File {path} is not unique")

    @classmethod
    def try_create(cls, db, path, rel_path, artist_id, album_id, track_id):
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO files (path, rel_path, artist_id, album_id, track_id)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
            """,
            (str(path), str(rel_path), artist_id, album_id, track_id))
        row = cursor.fetchone()
        db.commit()
        if row is None:
            return None

        return cls(
            id=row[0],
            path=path,
            rel_path=rel_path,
            artist_id=artist_id,
            album_id=album_id,
            track_id=track_id)
