import pytest
from sqlmodel import Session, SQLModel, create_engine, text

from seinpy.exporters.database import (
    DatabaseExporter,
    Episode,
    Rating,
    Script,
    insert_credit,
    insert_rating,
    insert_script,
)


@pytest.fixture
def in_memory_engine():
    """Create an in-memory SQLite database.

    Avoids creating files on disk for quick tests.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, future=True
    )
    # keep the connection open for the tests to supress resource warnings
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_insert_script(in_memory_engine, fake_script):
    with Session(in_memory_engine) as session:
        insert_script(session, fake_script)
        session.commit()

        # check that the episdoe was created
        episode = session.get(Episode, "S01E02")
        assert episode is not None
        assert episode.episode_id == "S01E02"
        assert episode.episode_num == 2
        assert episode.episode_title == "Episode 2."

        # check that the script was created
        script = session.get(Script, "S01E02")
        assert script is not None
        assert script.episode_id == "S01E02"

        # check that the script lines were created
        # not using session.get because it's a child of Script
        script_lines = session.exec(
            text("SELECT * FROM scriptline WHERE episode_id='S01E02'")
        ).all()
        assert len(script_lines) == 4
        assert script_lines[0].speaker == "Jerry"
        assert script_lines[0].dialogue == "Hi, I'm Jerry."
        assert script_lines[3].speaker == "Elaine"
        assert script_lines[3].dialogue == "Hi, I'm Elaine."


def test_insert_rating(in_memory_engine, fake_rating):
    with Session(in_memory_engine) as session:
        insert_rating(session, fake_rating)
        session.commit()

        # check that the episode was created
        episode = session.get(Episode, "S01E02")
        assert episode is not None
        assert episode.episode_id == "S01E02"
        assert episode.episode_num == 2
        assert episode.episode_title == "Episode 2."

        # check that the rating was created
        rating = session.get(Rating, "S01E02")
        assert rating is not None
        assert rating.episode_id == "S01E02"
        assert rating.rating == 10
        assert rating.num_votes == 100
        assert rating.link == "https://example.com"


def test_insert_credit(in_memory_engine, fake_credit):
    with Session(in_memory_engine) as session:
        insert_credit(session, fake_credit)
        session.commit()

        # check that the episode was created
        episode = session.get(Episode, "S01E02")
        assert episode is not None
        assert episode.episode_id == "S01E02"
        assert episode.episode_num == 2
        assert episode.episode_title == "Episode 2."

        people = session.exec(
            text("SELECT * FROM creditperson WHERE episode_id='S01E02'")
        ).all()
        assert len(people) == 8  # 2 writers + 2 directors + 4 actors

        # Check writers
        assert people[0].name == "Larry David"
        assert people[0].type == "writer"
        assert people[1].name == "Jerry Seinfeld"
        assert people[1].type == "writer"

        # Check directors
        assert people[2].name == "Jerry Seinfeld"
        assert people[2].type == "director"
        assert people[3].name == "Larry David"
        assert people[3].type == "director"

        # Check actors
        assert people[4].name == "Jerry Seinfeld"
        assert people[4].type == "actor"
        assert people[4].role == "Jerry"
        assert people[5].name == "Jason Alexander"
        assert people[5].type == "actor"
        assert people[5].role == "George"
        assert people[6].name == "Julia Louis-Dreyfus"
        assert people[6].type == "actor"
        assert people[6].role == "Elaine"
        assert people[7].name == "Michael Richards"
        assert people[7].type == "actor"
        assert people[7].role == "Kramer"


class TestDatabaseExporter:
    def test_export(self, fake_episode, tmp_path):
        """Test that DatabaseExporter.export creates a database with all data."""
        save_path = tmp_path / "test_export.db"
        exporter = DatabaseExporter()
        exporter.export([fake_episode], str(save_path))

        assert save_path.exists()

        # only check that the episode was created
        engine = create_engine(f"sqlite:///{save_path}")
        try:
            with Session(engine) as session:
                episode = session.get(Episode, "S01E02")
                assert episode is not None
                assert episode.episode_id == "S01E02"
                assert episode.episode_num == 2
                assert episode.episode_title == "Episode 2."
        finally:
            engine.dispose()

    def test_export_invalid_extension(self, fake_episode, tmp_path):
        """Test that DatabaseExporter.export raises ValueError for invalid file extension."""
        save_path = tmp_path / "test_export.txt"
        exporter = DatabaseExporter()
        with pytest.raises(ValueError, match="Save path must end with .db"):
            exporter.export([fake_episode], str(save_path))

    # idk why this one is giving resource warnings
    # @pytest.mark.filterwarnings("ignore::ResourceWarning")
    def test_export_multiple_episodes(self, fake_episode, tmp_path):
        """Test that DatabaseExporter.export handles multiple episodes."""
        save_path = tmp_path / "test_export.db"
        exporter = DatabaseExporter()
        # Export the same episode twice to test multiple episodes
        exporter.export([fake_episode, fake_episode], str(save_path))

        # Verify the database file was created
        assert save_path.exists()

        engine = create_engine(f"sqlite:///{save_path}")
        try:
            with Session(engine) as session:
                # Should still have one episode (same episode_id, so merged)
                episode = session.get(Episode, "S01E02")
                assert episode is not None
                assert episode.episode_id == "S01E02"
                assert episode.episode_num == 2
                assert episode.episode_title == "Episode 2."
        finally:
            engine.dispose()
