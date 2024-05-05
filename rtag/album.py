from dataclasses import dataclass
from rtag.entity import Entity
from rtag.error import ReportableError
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class Album(Entity):
    id: int
    artist_id: int
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
            CREATE TABLE IF NOT EXISTS albums
            (
                id INTEGER PRIMARY KEY NOT NULL,
                artist_id INTEGER NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                safe_title TEXT NOT NULL,
                disambiguator TEXT NULL,
                sort_title TEXT NULL,
                UNIQUE(artist_id, title, disambiguator)
                UNIQUE(artist_id, safe_title)
                FOREIGN KEY(artist_id) REFERENCES artists(id)
            );
            CREATE INDEX albums_uuid_idx ON albums(uuid);
            COMMIT;
            """)

    @classmethod
    def list_all(cls, db):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, artist_id, uuid, title, safe_title, disambiguator, sort_title FROM albums ORDER BY sort_title")
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                artist_id=row[1],
                uuid=UUID(row[2]),
                title=row[3],
                safe_title=row[4],
                disambiguator=row[5],
                sort_title=row[6])

    @classmethod
    def list(cls, db, artist_id):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, uuid, title, safe_title, disambiguator, sort_title FROM albums WHERE artist_id = ? ORDER BY sort_title",
            (artist_id, ))
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                artist_id=artist_id,
                uuid=UUID(row[1]),
                title=row[2],
                safe_title=row[3],
                disambiguator=row[4],
                sort_title=row[5])

    @classmethod
    def create(cls, db, artist_id, title, safe_title, disambiguator=None, sort_title=None):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO albums (artist_id, uuid, title, safe_title, disambiguator, sort_title)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (artist_id, str(uuid), title, safe_title, disambiguator, sort_title))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return cls(
                id=row[0],
                artist_id=artist_id,
                uuid=uuid,
                title=title,
                safe_title=safe_title,
                disambiguator=disambiguator,
                sort_title=sort_title)

        if disambiguator is None:
            m = f"Album \"{title}\" for artist ID {artist_id} is not unique: " \
                "specify a unique disambiguator"
        else:
            m = f"Album \"{title}\" with disambiguator " \
                f"\"{disambiguator}\" for artist ID {artist_id} is not unique: " \
                "specify a different disambiguator"
        raise ReportableError(m)

    @classmethod
    def get_by_id(cls, db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT artist_id, uuid, title, safe_title, disambiguator, sort_title FROM albums WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=id,
                artist_id=row[0],
                uuid=UUID(row[1]),
                title=row[2],
                safe_title=row[3],
                disambiguator=row[4],
                sort_title=row[5])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve album with ID {id}")

    @classmethod
    def get_by_uuid(cls, db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, artist_id, title, safe_title, disambiguator, sort_title FROM albums WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                artist_id=row[1],
                uuid=uuid,
                title=row[2],
                safe_title=row[3],
                disambiguator=row[4],
                sort_title=row[5])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve album with UUID {uuid}")

    @classmethod
    def query(cls, db, artist_id, title, disambiguator=None, default=_MISSING):
        cursor = db.cursor()
        if disambiguator is None:
            cursor.execute(
                """
                SELECT id, uuid, safe_title, sort_title FROM albums WHERE artist_id = ? AND title = ? AND disambiguator IS NULL
                """,
                (artist_id, title))
        else:
            cursor.execute(
                """
                SELECT id, uuid, safe_title, sort_title FROM albums WHERE artist_id = ? AND title = ? AND disambiguator = ?
                """,
                (artist_id, title, disambiguator))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                artist_id=artist_id,
                uuid=UUID(row[1]),
                title=title,
                safe_title=row[2],
                disambiguator=disambiguator,
                sort_title=row[3])

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve album ({title}, {disambiguator}) for artist ID {artist_id}")

    def update(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE albums
            SET title = ?, safe_title = ?, disambiguator = ?, sort_title = ?
            WHERE id = ?
            """,
            (self.title, self.safe_title, self.disambiguator, self.sort_title, self.id))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to update album with ID {self.id}")
        db.commit()
