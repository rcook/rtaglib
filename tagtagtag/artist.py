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
    fs_name: str
    disambiguator: str
    sort_name: str

    @staticmethod
    def create_schema(db):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS artists
            (
                id INTEGER PRIMARY KEY NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                fs_name TEXT NOT NULL UNIQUE,
                disambiguator TEXT NULL,
                sort_name TEXT NULL,
                UNIQUE(name, disambiguator)
            )
            """)

    @classmethod
    def list(cls, db):
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, uuid, name, fs_name, disambiguator, sort_name FROM artists ORDER BY sort_name")
        for row in cursor.fetchall():
            yield cls(
                id=row[0],
                uuid=UUID(row[1]),
                name=row[2],
                fs_name=row[3],
                disambiguator=row[4],
                sort_name=row[5])

    @classmethod
    def create(cls, db, name, fs_name, disambiguator=None, sort_name=None):
        uuid = uuid4()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO artists (uuid, name, fs_name, disambiguator, sort_name)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id
            """,
            (str(uuid), name, fs_name, disambiguator, sort_name))
        row = cursor.fetchone()
        db.commit()
        if row is not None:
            return cls(
                id=row[0],
                uuid=uuid,
                name=name,
                fs_name=fs_name,
                disambiguator=disambiguator,
                sort_name=sort_name)

        if disambiguator is None:
            m = f"Artist \"{name}\" with safe name \"{fs_name}\" is not unique: " \
                "specify a unique disambiguator"
        else:
            m = f"Artist \"{name}\" with safe name \"{fs_name}\" and disambiguator " \
                f"\"{disambiguator}\" is not unique: " \
                "specify a different disambiguator"
        raise ReportableError(m)

    @classmethod
    def get_by_id(cls, db, id, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT uuid, name, fs_name, disambiguator, sort_name FROM artists WHERE id = ?
            """,
            (id, ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=id,
                uuid=UUID(row[0]),
                name=row[1],
                fs_name=row[2],
                disambiguator=row[3],
                sort_name=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve artist with ID {id}")

    @classmethod
    def get_by_uuid(cls, db, uuid, default=_MISSING):
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, name, fs_name, disambiguator, sort_name FROM artists WHERE uuid = ?
            """,
            (str(uuid), ))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                uuid=uuid,
                name=row[1],
                fs_name=row[2],
                disambiguator=row[3],
                sort_name=row[4])

        if default is not _MISSING:
            return default

        raise RuntimeError(f"Could not retrieve artist with UUID {uuid}")

    @classmethod
    def query(cls, db, name, disambiguator=None, default=_MISSING):
        cursor = db.cursor()
        if disambiguator is None:
            cursor.execute(
                """
                SELECT id, uuid, fs_name, sort_name FROM artists WHERE name = ? AND disambiguator IS NULL
                """,
                (name, ))
        else:
            cursor.execute(
                """
                SELECT id, uuid, fs_name, sort_name FROM artists WHERE name = ? AND disambiguator = ?
                """,
                (name, disambiguator))
        row = cursor.fetchone()
        if row is not None:
            return cls(
                id=row[0],
                uuid=UUID(row[1]),
                name=name,
                fs_name=row[2],
                disambiguator=disambiguator,
                sort_name=row[3])

        if default is not _MISSING:
            return default

        raise RuntimeError(
            f"Could not retrieve artist ({name}, {disambiguator})")

    def update(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE artists
            SET name = ?, fs_name = ?, disambiguator = ?, sort_name = ?
            WHERE id = ?
            """,
            (self.name, self.fs_name, self.disambiguator, self.sort_name, self.id))
        if cursor.rowcount != 1:
            raise RuntimeError(f"Failed to update artist with ID {self.id}")
        db.commit()
