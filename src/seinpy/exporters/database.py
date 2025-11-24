"""Database writer."""

from pathlib import Path
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine
from seinpy.base import Exporter
import seinpy.schema as schema

###
# Define the SQL models
###


class Episode(SQLModel, table=True):
    episode_id: str = Field(primary_key=True)
    episode_num: Optional[int] = None
    episode_title: Optional[str] = None

    # define relationships
    # ie. ways to link the tables. tells sqlmodel how to connect rows across tables
    # back_populates creates bidirectional relationships.
    script: Optional["Script"] = Relationship(back_populates="episode")
    rating: Optional["Rating"] = Relationship(back_populates="episode")
    credit: Optional["Credit"] = Relationship(back_populates="episode")


class Script(SQLModel, table=True):
    episode_id: str = Field(foreign_key="episode.episode_id", primary_key=True)
    episode: Optional["Episode"] = Relationship(back_populates="script")

    lines: List["ScriptLine"] = Relationship(back_populates="script")


class ScriptLine(SQLModel, table=True):
    # id is optional because sqlite autogenerates it because it's the primary key.
    # this is because ScriptLine is a child of Script
    id: Optional[int] = Field(default=None, primary_key=True)
    episode_id: str = Field(foreign_key="script.episode_id")
    speaker: str
    dialogue: str

    script: Optional[Script] = Relationship(back_populates="lines")


class Rating(SQLModel, table=True):
    episode_id: str = Field(foreign_key="episode.episode_id", primary_key=True)
    rating: Optional[float] = None
    num_votes: Optional[int] = None
    link: Optional[str] = None

    episode: Optional["Episode"] = Relationship(back_populates="rating")


class Credit(SQLModel, table=True):
    episode_id: str = Field(foreign_key="episode.episode_id", primary_key=True)
    description: Optional[str] = None
    date: Optional[str] = None

    episode: Optional["Episode"] = Relationship(back_populates="credit")
    people: List["CreditPerson"] = Relationship(back_populates="credit")


class CreditPerson(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    episode_id: str = Field(foreign_key="credit.episode_id")
    type: str  # writer, director, actor
    name: str
    role: Optional[str] = None  # only for actors

    credit: Optional["Credit"] = Relationship(back_populates="people")


###
# Define the inserting functions
###


def insert_script(session: Session, script: Script) -> None:
    """Insert a Pydantic Script object into the DB."""
    # Ensure Episode exists
    episode = Episode(
        episode_id=script.ref.episode_id,
        episode_num=script.ref.episode_num,
        episode_title=script.ref.episode_title,
    )
    session.merge(episode)

    script_row = Script(episode_id=script.ref.episode_id)
    session.merge(script_row)

    for line in script.script_lines:
        session.add(
            ScriptLine(
                episode_id=script.ref.episode_id,
                speaker=line.speaker,
                dialogue=line.dialogue,
            )
        )


def insert_rating(session: Session, rating: Rating) -> None:
    """Insert a Pydantic Rating object into the DB."""
    # Ensure Episode exists
    episode = Episode(
        episode_id=rating.ref.episode_id,
        episode_num=rating.ref.episode_num,
        episode_title=rating.ref.episode_title,
    )
    session.merge(episode)

    # Insert rating
    rating_row = Rating(
        episode_id=rating.ref.episode_id,
        rating=rating.rating,
        num_votes=rating.num_votes,
        link=rating.link,
    )
    session.merge(rating_row)


def insert_credit(session: Session, credit: Credit) -> None:
    """Insert a Pydantic Credit object into the DB."""
    # Ensure Episode exists
    episode = Episode(
        episode_id=credit.ref.episode_id,
        episode_num=credit.ref.episode_num,
        episode_title=credit.ref.episode_title,
    )
    session.merge(episode)

    credit_row = Credit(
        episode_id=credit.ref.episode_id,
        description=credit.description,
        date=credit.date,
    )
    session.merge(credit_row)

    def add_credit_people(
        type_: str, people: List[schema.Writer | schema.Director | schema.Actor]
    ) -> None:
        if not people:
            return
        for person in people:
            session.add(
                CreditPerson(
                    episode_id=credit.ref.episode_id,
                    type=type_,
                    name=person.name,
                    role=getattr(person, "role", None),  # only for actors
                )
            )

    add_credit_people("writer", credit.writers)
    add_credit_people("director", credit.directors)
    add_credit_people("actor", credit.actors)


###
# Define the Exporter
###


class DatabaseExporter(Exporter):
    """Write the data to a database."""

    def export(self, data: List[Episode], save_path: str) -> None:
        """Export the data to a database."""
        f = Path(save_path)
        if not f.suffix == ".db":
            raise ValueError("Save path must end with .db")
        if not str(f).startswith("sqlite:///"):
            f = f"sqlite:///{f}"
        engine = create_engine(str(f))
        try:
            SQLModel.metadata.create_all(engine)

            with Session(engine) as session:
                for episode in data:
                    insert_script(session, episode.script)
                    insert_rating(session, episode.rating)
                    insert_credit(session, episode.credit)
                session.commit()
        finally:
            engine.dispose()
