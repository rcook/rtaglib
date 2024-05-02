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
    title: str
    safe_title: str
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
                title TEXT NOT NULL,
                safe_title TEXT NOT NULL,
                number INTEGER NULL,
                UNIQUE(album_id, number)
                FOREIGN KEY(album_id) REFERENCES albums(id)
            )
            """)

    @classmethod
    def list(cls, db, album_id):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, uuid, title, safe_title, number FROM tracks WHERE album_id = ? ORDER BY number",
            (album_id, ))
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                album_id=album_id,
                uuid=UUID(row[1]),
                title=row[2],
                safe_title=row[3],
                number=row[4])

    @classmethod
    def create(cls, db, album_id, title, safe_title, number):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO tracks (album_id, uuid, title, safe_title, number)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
            """,
            (album_id, str(uuid), title, safe_title, number))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return cls(
                id=row[0],
                album_id=album_id,
                uuid=uuid,
                title=title,
                safe_title=safe_title,
                number=number)

        if number is None:
            m = f"Track \"{title}\" " \
                f"for album ID {album_id} is not unique"
        else:
            m = f"Track \"{title}\" with number {number} " \
                f"for album ID {album_id} is not unique"
        raise ReportableError(m)

    @classmethod
    def get_by_id(cls, db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT album_id, uuid, title, safe_title, number FROM tracks WHERE id = ?
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
                number=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve track with ID {id}")

    @classmethod
    def get_by_uuid(cls, db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, album_id, title, safe_title, number FROM tracks WHERE uuid = ?
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
                number=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve track with UUID {uuid}")

    @classmethod
    def query(cls, db, album_id, title, number, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, uuid, safe_title FROM tracks WHERE album_id = ? AND title = ? AND number = ?
            """,
            (album_id, title, number))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                album_id=album_id,
                uuid=UUID(row[1]),
                title=title,
                safe_title=row[2],
                number=number)

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve track ({title}, {number}) for album ID {album_id}")

    def update(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE tracks
            SET title = ?, safe_title = ?, number = ?
            WHERE id = ?
            """,
            (self.title, self.safe_name, self.number, self.id))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to update track with ID {self.id}")
        db.commit()
