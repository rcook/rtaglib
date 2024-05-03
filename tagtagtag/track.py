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
    disc: int
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
                disc INTEGER NULL,
                number INTEGER NULL,
                UNIQUE(album_id, disc, number)
                FOREIGN KEY(album_id) REFERENCES albums(id)
            )
            """)

    @classmethod
    def list(cls, db, album_id):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, uuid, title, safe_title, disc, number FROM tracks WHERE album_id = ? ORDER BY number",
            (album_id, ))
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                album_id=album_id,
                uuid=UUID(row[1]),
                title=row[2],
                safe_title=row[3],
                disc=row[4],
                number=row[5])

    @classmethod
    def create(cls, db, album_id, title, safe_title, disc, number):
        track = cls.try_create(
            db=db,
            album_id=album_id,
            title=title,
            safe_title=safe_title,
            disc=disc,
            number=number)
        if track is not None:
            return track

        parts = [f"Track \"{title}\""]

        if disc is not None:
            parts.append(f" (disc {disc})")

        if number is not None:
            parts.append(f"(number {number})")

        raise ReportableError(
            " ".join(parts) + f" for album ID {album_id} is not unique")

    @classmethod
    def try_create(cls, db, album_id, title, safe_title, disc, number):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO tracks (album_id, uuid, title, safe_title, disc, number)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (album_id, str(uuid), title, safe_title, disc, number))
        row = cursor.fetchone()
        db.commit()
        if row is None:
            return None

        return cls(
            id=row[0],
            album_id=album_id,
            uuid=uuid,
            title=title,
            safe_title=safe_title,
            disc=disc,
            number=number)

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

    def update(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE tracks
            SET title = ?, safe_title = ?, disc = ?, number = ?
            WHERE id = ?
            """,
            (self.title, self.safe_title, self.disc, self.number, self.id))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to update track with ID {self.id}")
        db.commit()
