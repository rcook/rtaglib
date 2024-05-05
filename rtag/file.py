from dataclasses import dataclass
from rtag.entity import Entity
from rtag.error import ReportableError
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class File(Entity):
    id: int
    path: str
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
                artist_id INTEGER NOT NULL,
                album_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                UNIQUE(artist_id, album_id, track_id)
                FOREIGN KEY(album_id) REFERENCES albums(id)
            );
            CREATE INDEX IF NOT EXISTS files_artist_id_idx ON files(artist_id);
            CREATE INDEX IF NOT EXISTS files_album_id_idx ON files(album_id);
            CREATE INDEX IF NOT EXISTS files_track_id_idx ON files(track_id);
            COMMIT;
            """)

    @classmethod
    def create(cls, db, path, artist_id, album_id, track_id):
        file = cls.try_create(
            db=db,
            path=path,
            artist_id=artist_id,
            album_id=album_id,
            track_id=track_id)
        if file is not None:
            return file

        raise ReportableError(f"File {path} is not unique")

    @classmethod
    def try_create(cls, db, path, artist_id, album_id, track_id):
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO files (path, artist_id, album_id, track_id)
            VALUES (?, ?, ?, ?)
            RETURNING id
            """,
            (path, artist_id, album_id, track_id))
        row = cursor.fetchone()
        db.commit()
        if row is None:
            return None

        return cls(
            id=row[0],
            path=path,
            artist_id=artist_id,
            album_id=album_id,
            track_id=track_id)

    @classmethod
    def get_by_id(cls, db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT album_id, uuid, title, safe_title, disc, number FROM tracks WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=id,
                album_id=row[0],
                uuid=UUID(row[1]),
                title=row[2],
                safe_title=row[3],
                disc=row[4],
                number=row[5])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve track with ID {id}")

    @classmethod
    def get_by_uuid(cls, db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, album_id, title, safe_title, disc, number FROM tracks WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                album_id=row[1],
                uuid=uuid,
                title=row[2],
                safe_title=row[3],
                disc=row[4],
                number=row[5])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve track with UUID {uuid}")

    @classmethod
    def query(cls, db, album_id, title, disc, number, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, uuid, safe_title
            FROM tracks
            WHERE album_id = ? AND title = ? AND disc = ? AND number = ?
            """,
            (album_id, title, disc, number))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                album_id=album_id,
                uuid=UUID(row[1]),
                title=title,
                safe_title=row[2],
                disc=disc,
                number=number)

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve track ({title}, {number}) for album ID {album_id}")
