from dataclasses import dataclass
from rpycli.prelude import *
from rtag.entity import Entity
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class Artist(Entity):
    id: int
    uuid: UUID
    title: str
    safe_title: str
    disambiguator: str
    sort_title: str

    @staticmethod
    def create_schema(db):
        db.executescript(
            """
            BEGIN;
            CREATE TABLE IF NOT EXISTS artists
            (
                id INTEGER PRIMARY KEY NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                safe_title TEXT NOT NULL UNIQUE,
                disambiguator TEXT NULL,
                sort_title TEXT NULL,
                UNIQUE(title, disambiguator)
            );
            CREATE INDEX IF NOT EXISTS artists_uuid_idx ON artists(uuid);
            COMMIT;
            """)

    @classmethod
    def list(cls, db):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, uuid, title, safe_title, disambiguator, sort_title FROM artists ORDER BY sort_title")
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                uuid=UUID(row[1]),
                title=row[2],
                safe_title=row[3],
                disambiguator=row[4],
                sort_title=row[5])

    @classmethod
    def create(cls, db, title, safe_title, disambiguator=None, sort_title=None):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO artists (uuid, title, safe_title, disambiguator, sort_title)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
            """,
            (str(uuid), title, safe_title, disambiguator, sort_title))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return cls(
                id=row[0],
                uuid=uuid,
                title=title,
                safe_title=safe_title,
                disambiguator=disambiguator,
                sort_title=sort_title)

        if disambiguator is None:
            m = f"Artist \"{title}\" with safe title \"{safe_title}\" is not unique: " \
                "specify a unique disambiguator"
        else:
            m = f"Artist \"{title}\" with safe title \"{safe_title}\" and disambiguator " \
                f"\"{disambiguator}\" is not unique: " \
                "specify a different disambiguator"
        raise ReportableError(m)

    @classmethod
    def get_by_id(cls, db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT uuid, title, safe_title, disambiguator, sort_title FROM artists WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=id,
                uuid=UUID(row[0]),
                title=row[1],
                safe_title=row[2],
                disambiguator=row[3],
                sort_title=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve artist with ID {id}")

    @classmethod
    def get_by_uuid(cls, db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, title, safe_title, disambiguator, sort_title FROM artists WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                uuid=uuid,
                title=row[1],
                safe_title=row[2],
                disambiguator=row[3],
                sort_title=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve artist with UUID {uuid}")

    @classmethod
    def query(cls, db, title, disambiguator=None, default=_MISSING):
        cursor = db.cursor()
        if disambiguator is None:
            cursor.execute(
                """
                SELECT id, uuid, safe_title, sort_title FROM artists WHERE title = ? AND disambiguator IS NULL
                """,
                (title, ))
        else:
            cursor.execute(
                """
                SELECT id, uuid, safe_title, sort_title FROM artists WHERE title = ? AND disambiguator = ?
                """,
                (title, disambiguator))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                uuid=UUID(row[1]),
                title=title,
                safe_title=row[2],
                disambiguator=disambiguator,
                sort_title=row[3])

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve artist ({title}, {disambiguator})")

    def update(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE artists
            SET title = ?, safe_title = ?, disambiguator = ?, sort_title = ?
            WHERE id = ?
            """,
            (self.title, self.safe_title, self.disambiguator, self.sort_title, self.id))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to update artist with ID {self.id}")
        db.commit()
