from dataclasses import dataclass
from tagtagtag.entity import Entity
from tagtagtag.error import ReportableError
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class Track(Entity):
    id: int
    album_id: int
    uuid: UUID
    name: str
    fs_name: str
    number: int

    @staticmethod
    def create_schema(db):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tracks
            (
                id INTEGER PRIMARY KEY NOT NULL,
                album_id INTEGER NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                fs_name TEXT NOT NULL,
                number INTEGER NULL,
                UNIQUE(album_id, number)
                FOREIGN KEY(album_id) REFERENCES albums(id)
            )
            """)

    @classmethod
    def list(cls, db, album_id):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, uuid, name, fs_name, number FROM tracks WHERE album_id = ? ORDER BY number",
            (album_id, ))
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                album_id=album_id,
                uuid=UUID(row[1]),
                name=row[2],
                fs_name=row[3],
                number=row[4])

    @classmethod
    def create(cls, db, album_id, name, fs_name, number):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO tracks (album_id, uuid, name, fs_name, number)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
            """,
            (album_id, str(uuid), name, fs_name, number))
        print((album_id, str(uuid), name, fs_name, number))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return cls(
                id=row[0],
                album_id=album_id,
                uuid=uuid,
                name=name,
                fs_name=fs_name,
                number=number)

        if number is None:
            m = f"Track \"{name}\" " \
                f"for album ID {album_id} is not unique"
        else:
            m = f"Track \"{name}\" with number {number} " \
                f"for album ID {album_id} is not unique"
        raise ReportableError(m)

    @classmethod
    def get_by_id(cls, db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT album_id, uuid, name, fs_name, number FROM tracks WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=id,
                album_id=row[0],
                uuid=UUID(row[1]),
                name=row[2],
                fs_name=row[3],
                number=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve track with ID {id}")

    @classmethod
    def get_by_uuid(cls, db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, album_id, name, fs_name, number FROM tracks WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                album_id=row[1],
                uuid=uuid,
                name=row[2],
                fs_name=row[3],
                number=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve track with UUID {uuid}")

    @classmethod
    def query(cls, db, album_id, name, number, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, uuid, fs_name FROM tracks WHERE album_id = ? AND name = ? AND number = ?
            """,
            (album_id, name, number))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                album_id=album_id,
                uuid=UUID(row[1]),
                name=name,
                fs_name=row[2],
                number=number)

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve track ({name}, {number}) for album ID {album_id}")

    def update(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE tracks
            SET name = ?, fs_name = ?, number = ?
            WHERE id = ?
            """,
            (self.name, self.fs_name, self.number, self.id))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to update track with ID {self.id}")
        db.commit()
