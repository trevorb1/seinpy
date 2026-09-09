"""Database writer."""

from pathlib import Path
from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, text

import seinpy.schema as schema
from seinpy.base import Exporter

###
# Define the SQL models
###


class Episode(SQLModel, table=True):
    episode_id: str = Field(primary_key=True)
    episode_num: int | None = None
    episode_title: str | None = None

    # define relationships
    # tells sqlmodel how to connect rows across tables
    # back_populates creates bidirectional relationships.
    script: Optional["Script"] = Relationship(back_populates="episode")
    rating: Optional["Rating"] = Relationship(back_populates="episode")
    credit: Optional["Credit"] = Relationship(back_populates="episode")


class Script(SQLModel, table=True):
    episode_id: str = Field(foreign_key="episode.episode_id", primary_key=True)
    episode: Optional["Episode"] = Relationship(back_populates="script")

    lines: list["ScriptLine"] = Relationship(back_populates="script")


class ScriptLine(SQLModel, table=True):
    __tablename__ = "scriptline"

    # id is optional because sqlite autogenerates it because it's the primary key.
    # this is because ScriptLine is a child of Script
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    episode_id: str = Field(foreign_key="script.episode_id", index=True)
    speaker: str
    dialogue: str

    script: Optional["Script"] = Relationship(back_populates="lines")


class Rating(SQLModel, table=True):
    episode_id: str = Field(foreign_key="episode.episode_id", primary_key=True)
    rating: float | None = None
    num_votes: int | None = None
    link: str | None = None

    episode: Optional["Episode"] = Relationship(back_populates="rating")


class Credit(SQLModel, table=True):
    episode_id: str = Field(foreign_key="episode.episode_id", primary_key=True)
    description: str | None = None
    date: str | None = None

    episode: Optional["Episode"] = Relationship(back_populates="credit")
    people: list["CreditPerson"] = Relationship(back_populates="credit")


class CreditPerson(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    episode_id: str = Field(foreign_key="credit.episode_id", index=True)
    type: str  # writer, director, actor
    name: str
    role: str | None = None  # only for actors

    credit: Optional["Credit"] = Relationship(back_populates="people")


###
# Define the inserting functions
###


def _upsert_episode_stub(session: Session, ref: schema.EpisodeRef) -> None:
    """Ensure the Episode row exists before adding child foreign keys."""
    if not ref or not ref.episode_id:
        return
    episode = Episode(
        episode_id=ref.episode_id,
        episode_num=ref.episode_num,
        episode_title=ref.episode_title,
    )
    session.merge(episode)


def insert_script(session: Session, script: schema.Script) -> None:
    """Insert a Pydantic Script object into the DB."""
    if not script or not script.ref or not script.ref.episode_id:
        return

    _upsert_episode_stub(session, script.ref)

    script_row = Script(episode_id=script.ref.episode_id)
    session.merge(script_row)

    # Batch add script lines for performance
    lines = [
        ScriptLine(
            episode_id=script.ref.episode_id,
            speaker=line.speaker,
            dialogue=line.dialogue,
        )
        for line in script.script_lines
    ]
    session.add_all(lines)


def insert_rating(session: Session, rating: schema.Rating) -> None:
    """Insert a Pydantic Rating object into the DB."""
    # Ensure Episode exists
    if not rating or not rating.ref or not rating.ref.episode_id:
        return

    _upsert_episode_stub(session, rating.ref)

    rating_row = Rating(
        episode_id=rating.ref.episode_id,
        rating=rating.rating,
        num_votes=rating.num_votes,
        link=rating.link,
    )
    session.merge(rating_row)


def insert_credit(session: Session, credit: schema.Credit) -> None:
    """Insert a Pydantic Credit object into the DB."""
    # Ensure Episode exists
    if not credit or not credit.ref or not credit.ref.episode_id:
        return

    _upsert_episode_stub(session, credit.ref)

    credit_row = Credit(
        episode_id=credit.ref.episode_id,
        description=credit.description,
        date=credit.date,
    )
    session.merge(credit_row)

    people_to_add: list[CreditPerson] = []

    def add_credit_people(type_: str, people: list | None) -> None:
        if not people:
            return
        for person in people:
            people_to_add.append(
                CreditPerson(
                    episode_id=credit.ref.episode_id,
                    type=type_,
                    name=person.name,
                    role=getattr(person, "role", None),
                )
            )

    add_credit_people("writer", credit.writers)
    add_credit_people("director", credit.directors)
    add_credit_people("actor", credit.actors)

    if people_to_add:
        session.add_all(people_to_add)


###
# Full-Text Search (FTS5) DDL
###

FTS_SETUP_SQL = """
-- Create FTS5 virtual table indexing script lines
CREATE VIRTUAL TABLE IF NOT EXISTS scriptline_fts USING fts5(
    speaker,
    dialogue,
    content='scriptline',
    content_rowid='id',
    tokenize='porter unicode61'
);

-- Triggers to maintain sync on future writes/updates
CREATE TRIGGER IF NOT EXISTS trg_scriptline_ai AFTER INSERT ON scriptline BEGIN
    INSERT INTO scriptline_fts(rowid, speaker, dialogue)
    VALUES (new.id, new.speaker, new.dialogue);
END;

CREATE TRIGGER IF NOT EXISTS trg_scriptline_ad AFTER DELETE ON scriptline BEGIN
    INSERT INTO scriptline_fts(scriptline_fts, rowid, speaker, dialogue)
    VALUES ('delete', old.id, old.speaker, old.dialogue);
END;

CREATE TRIGGER IF NOT EXISTS trg_scriptline_au AFTER UPDATE ON scriptline BEGIN
    INSERT INTO scriptline_fts(scriptline_fts, rowid, speaker, dialogue)
    VALUES ('delete', old.id, old.speaker, old.dialogue);
    INSERT INTO scriptline_fts(rowid, speaker, dialogue)
    VALUES (new.id, new.speaker, new.dialogue);
END;
"""

###
# Define the Exporter
###


class DatabaseExporter(Exporter):
    """Write the data to a SQLite database with FTS5 search index."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DatabaseExporter):
            return NotImplemented
        return True

    def export(self, data: list[schema.Episode], save_path: str | Path) -> None:
        """Export the data to a database file with an optimized search index.

        If the database file already exists, it is overwritten to prevent
        duplicate records.

        Args:
            data: A list of Episode objects to export.
            save_path: Destination path ending with .db.

        Raises:
            ValueError: If the save path does not end with .db.
        """
        path = Path(save_path).resolve()
        if path.suffix != ".db":
            raise ValueError("Save path must end with .db")

        if path.exists():
            path.unlink()

        # build SQLite connection URL
        engine = create_engine(f"sqlite:///{path.as_posix()}")

        try:
            # initialize relational tables defined by SQLModel
            SQLModel.metadata.create_all(engine)

            # insert all episodes within a single transactional session
            with Session(engine) as session:
                for episode in data:
                    insert_script(session, episode.script)
                    insert_rating(session, episode.rating)
                    insert_credit(session, episode.credit)
                session.commit()

            # setup FTS5 virtual table, triggers, and populate the index
            with engine.connect() as conn:
                conn.connection.executescript(FTS_SETUP_SQL)
                # populate existing rows inserted by SQLModel
                conn.execute(
                    text(
                        "INSERT INTO scriptline_fts(scriptline_fts) VALUES('rebuild');"
                    )
                )
                conn.execute(
                    text(
                        "INSERT INTO scriptline_fts(scriptline_fts) VALUES('optimize');"
                    )
                )
                conn.commit()

            # vacuum to defragment and reduce file size for deployment
            with engine.connect() as conn:
                # SQLite requires autocommit for VACUUM
                conn.connection.isolation_level = None
                conn.execute(text("VACUUM;"))
        finally:
            engine.dispose()


# class DatabaseExporter(Exporter):
#     """Write the data to a database."""

#     def __eq__(self, other: object) -> bool:
#         """Check equality with another DatabaseExporter instance."""
#         if not isinstance(other, DatabaseExporter):
#             return NotImplemented
#         return True

#     def export(self, data: list[schema.Episode], save_path: str) -> None:
#         """Export the data to a database."""
#         f = Path(save_path)
#         if not f.suffix == ".db":
#             raise ValueError("Save path must end with .db")
#         if not str(f).startswith("sqlite:///"):
#             f = f"sqlite:///{f}"
#         engine = create_engine(str(f))
#         try:
#             SQLModel.metadata.create_all(engine)

#             with Session(engine) as session:
#                 for episode in data:
#                     insert_script(session, episode.script)
#                     insert_rating(session, episode.rating)
#                     insert_credit(session, episode.credit)
#                 session.commit()
#         finally:
#             engine.dispose()
