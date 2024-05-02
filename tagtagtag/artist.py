from dataclasses import dataclass
from tagtagtag.entity import Entity
from tagtagtag.error import ReportableError
from uuid import UUID, uuid4


_MISSING = object()


@dataclass(frozen=True)
class Artist(Entity):
    id: int
    uuid: UUID
    name: str
    sort_name: str
    fs_name: str
    disambiguator: str

    @staticmethod
    def create_schema(db):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS artists
            (
                id INTEGER PRIMARY KEY NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                sort_name TEXT NOT NULL,
                fs_name TEXT NOT NULL UNIQUE,
                disambiguator TEXT NULL,
                UNIQUE(name, disambiguator)
            )
            """)

    @staticmethod
    def create(db, name, sort_name, fs_name, disambiguator=None):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO artists (uuid, name, sort_name, fs_name, disambiguator)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, uuid
            """,
            (str(uuid), name, sort_name, fs_name, disambiguator))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return Artist(
                id=row[0],
                uuid=UUID(row[1]),
                name=name,
                sort_name=sort_name,
                fs_name=fs_name,
                disambiguator=disambiguator)

        if disambiguator is None:
            m = f"Artist \"{name}\" is not unique: " \
                "specify a unique disambiguator"
        else:
            m = f"Artist \"{name}\" with disambiguator " \
                f"\"{disambiguator}\" is not unique: " \
                "specify a different disambiguator"
        raise ReportableError(m)

    @staticmethod
    def get_by_id(db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT uuid, name, sort_name, fs_name, disambiguator FROM artists WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return Artist(
                id=id,
                uuid=UUID(row[0]),
                name=row[1],
                sort_name=row[2],
                fs_name=row[3],
                disambiguator=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve artist with ID {id}")

    @staticmethod
    def get_by_uuid(db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, name, sort_name, fs_name, disambiguator FROM artists WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return Artist(
                id=row[0],
                uuid=uuid,
                name=row[1],
                sort_name=row[2],
                fs_name=row[3],
                disambiguator=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve artist with UUID {uuid}")

    @staticmethod
    def get_by_name(db, name, disambiguator=None, default=_MISSING):
        cursor = db.cursor()
        if disambiguator is None:
            cursor.execute(
                """
                SELECT id, uuid, sort_name, fs_name FROM artists WHERE name = ? AND disambiguator IS NULL
                """,
                (name, ))
        else:
            cursor.execute(
                """
                SELECT id, uuid, sort_name, fs_name FROM artists WHERE name = ? AND disambiguator = ?
                """,
                (name, disambiguator))
        row = cursor.fetchone()
        if row is not None:
            return Artist(
                id=row[0],
                uuid=UUID(row[1]),
                name=name,
                sort_name=row[2],
                fs_name=row[3],
                disambiguator=disambiguator)

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve artist ({name}, {disambiguator})")
