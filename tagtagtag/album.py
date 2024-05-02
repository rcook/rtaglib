from dataclasses import dataclass
from tagtagtag.entity import Entity
from tagtagtag.error import ReportableError
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class Album(Entity):
    id: int
    artist_id: int
    uuid: UUID
    name: str
    fs_name: str
    disambiguator: str
    sort_name: str

    @staticmethod
    def create_schema(db):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS albums
            (
                id INTEGER PRIMARY KEY NOT NULL,
                artist_id INTEGER NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                fs_name TEXT NOT NULL UNIQUE,
                disambiguator TEXT NULL,
                sort_name TEXT NULL,
                UNIQUE(artist_id, name, disambiguator)
                FOREIGN KEY(artist_id) REFERENCES artists(id)
            )
            """)

    @staticmethod
    def create(db, artist_id, name, fs_name, disambiguator=None, sort_name=None):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO albums (artist_id, uuid, name, fs_name, disambiguator, sort_name)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (artist_id, str(uuid), name, fs_name, disambiguator, sort_name))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return Album(
                id=row[0],
                artist_id=artist_id,
                uuid=uuid,
                name=name,
                fs_name=fs_name,
                disambiguator=disambiguator,
                sort_name=sort_name)

        if disambiguator is None:
            m = f"Album \"{name}\" for artist ID {artist_id} is not unique: " \
                "specify a unique disambiguator"
        else:
            m = f"Album \"{name}\" with disambiguator " \
                f"\"{disambiguator}\" for artist ID {artist_id} is not unique: " \
                "specify a different disambiguator"
        raise ReportableError(m)

    @staticmethod
    def get_by_id(db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT artist_id, uuid, name, fs_name, disambiguator, sort_name FROM albums WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return Album(
                id=id,
                artist_id=row[0],
                uuid=UUID(row[1]),
                name=row[2],
                fs_name=row[3],
                disambiguator=row[4],
                sort_name=row[5])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve album with ID {id}")

    @staticmethod
    def get_by_uuid(db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, artist_id, name, fs_name, disambiguator, sort_name FROM albums WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return Album(
                id=row[0],
                artist_id=row[1],
                uuid=uuid,
                name=row[2],
                fs_name=row[3],
                disambiguator=row[4],
                sort_name=row[5])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve album with UUID {uuid}")

    @staticmethod
    def query(db, artist_id, name, disambiguator=None, default=_MISSING):
        cursor = db.cursor()
        if disambiguator is None:
            cursor.execute(
                """
                SELECT id, uuid, fs_name, sort_name FROM albums WHERE artist_id = ? AND name = ? AND disambiguator IS NULL
                """,
                (artist_id, name))
        else:
            cursor.execute(
                """
                SELECT id, uuid, fs_name, sort_name FROM albums WHERE artist_id = ? AND name = ? AND disambiguator = ?
                """,
                (artist_id, name, disambiguator))
        row = cursor.fetchone()
        if row is not None:
            return Album(
                id=row[0],
                artist_id=artist_id,
                uuid=UUID(row[1]),
                name=name,
                fs_name=row[2],
                disambiguator=disambiguator,
                sort_name=row[3])

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve album ({name}, {disambiguator}) for artist ID {artist_id}")
