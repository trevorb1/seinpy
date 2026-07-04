import pytest
from seinpy.context import (
    Context,
    ScriptExtractor,
    CreditExtractor,
    RatingExtractor,
    Exporter,
    read_episodes,
    _get_script_extractor,
    _get_credit_extractor,
    _get_rating_extractor,
    _get_exporter,
)
from seinpy.scripts.kaggle import KaggleScriptExtractor
from seinpy.credits.omdb import OMDBCreditExtractor
from seinpy.ratings.omdb import OMDBRatingExtractor
from seinpy.exporters.database import DatabaseExporter
from seinpy.exporters.csv import CsvExporter
from seinpy.exporters.json import JsonExporter
from seinpy.schema import (
    Director,
    Episode,
    Script,
    Credit,
    Rating,
    EpisodeRef,
    ScriptLine,
    Actor,
    Writer,
)
from seinpy.scripts.empty import EmptyScriptExtractor
from seinpy.credits.empty import EmptyCreditExtractor
from seinpy.ratings.empty import EmptyRatingExtractor



@pytest.fixture
def context(
    dummy_script_extractor,
    dummy_credit_extractor,
    dummy_rating_extractor,
    dummy_exporter,
):
    return Context(
        script_extractor=dummy_script_extractor,
        credit_extractor=dummy_credit_extractor,
        rating_extractor=dummy_rating_extractor,
        exporter=dummy_exporter,
    )


class TestContextProperties:
    def test_initial_properties(
        self,
        context,
    ):
        assert isinstance(context.script_extractor, ScriptExtractor)
        assert isinstance(context.credit_extractor, CreditExtractor)
        assert isinstance(context.rating_extractor, RatingExtractor)
        assert isinstance(context.exporter, Exporter)

    def test_set_script_extractor(self, context, dummy_script_extractor):
        new_extractor = dummy_script_extractor
        context.script_extractor = new_extractor
        assert context.script_extractor is new_extractor

    def test_set_credit_extractor(self, context, dummy_credit_extractor):
        new_extractor = dummy_credit_extractor
        context.credit_extractor = new_extractor
        assert context.credit_extractor is new_extractor

    def test_set_rating_extractor(self, context, dummy_rating_extractor):
        new_extractor = dummy_rating_extractor
        context.rating_extractor = new_extractor
        assert context.rating_extractor is new_extractor

    def test_set_exporter(self, context, dummy_exporter):
        new_exporter = dummy_exporter
        context.exporter = new_exporter
        assert context.exporter is new_exporter


class TestContext:
    expected_script = Script(
        ref=EpisodeRef(
            episode_id="S01E02",
            episode_num=2,
            episode_title="Episode 2",
        ),
        script_lines=[
            ScriptLine(speaker="Jerry", dialogue="Hi, I'm Jerry."),
            ScriptLine(speaker="George", dialogue="Hi, I'm George."),
            ScriptLine(speaker="Kramer", dialogue="Hi, I'm Kramer."),
            ScriptLine(speaker="Elaine", dialogue="Hi, I'm Elaine."),
        ],
    )

    expected_credit = Credit(
        ref=EpisodeRef(
            episode_id="S01E02",
            episode_num=2,
            episode_title="Episode 2",
        ),
        description="Seinfeld is literally a show about nothing.",
        date="2025-01-01",
        writers=[Writer(name="Larry David"), Writer(name="Jerry Seinfeld")],
        directors=[Director(name="Jerry Seinfeld"), Director(name="Larry David")],
        actors=[
            Actor(name="Jerry Seinfeld", role="Jerry"),
            Actor(name="Jason Alexander", role="George"),
            Actor(name="Julia Louis-Dreyfus", role="Elaine"),
            Actor(name="Michael Richards", role="Kramer"),
        ],
    )

    expected_rating = Rating(
        ref=EpisodeRef(
            episode_id="S01E02",
            episode_num=2,
            episode_title="Episode 2",
        ),
        rating=10,
        num_votes=100,
        link="https://www.imdb.com/",
    )

    expected_episode = Episode(
        script=expected_script,
        credit=expected_credit,
        rating=expected_rating,
    )

    def test_get_episode(self, context):
        actual = context._get_episode(episode_id="S01E02")
        print(actual)
        expected = self.expected_episode
        assert actual == expected

    def test_get_episode_empty(self, context):
        with pytest.raises(ValueError):
            context._get_episode()

    def test_get_episodes_by_ids(self, context):
        actual = context._get_episodes(episode_ids=["S01E02", "S01E02"])
        expected = [
            self.expected_episode,
            self.expected_episode,
        ]
        assert actual == expected

    def test_get_episodes_by_nums(self, context):
        actual = context._get_episodes(episode_nums=[2, 2])
        expected = [
            self.expected_episode,
            self.expected_episode,
        ]
        assert actual == expected

    def test_get_episodes_by_titles(self, context):
        actual = context._get_episodes(episode_titles=["Episode 2", "Episode 2"])
        expected = [
            context._get_episode(episode_title="Episode 2"),
            context._get_episode(episode_title="Episode 2"),
        ]
        assert actual == expected

    def test_get_episodes_by_seasons(self, context, metadata):
        actual = context._get_episodes(seasons=[1], metadata=metadata)
        expected = [
            context._get_episode(episode_id="S01E02"),
        ]
        assert len(actual) == 3  # length of metadata for season 1
        assert actual[0] == expected[0]

    def test_get_episodes_empty(self, context):
        with pytest.raises(ValueError):
            context._get_episodes()

    @pytest.mark.parametrize(
        "episode_ids",
        [("S01E01"), (["S01E01"])],
    )
    def test_read_by_ids(self, context, metadata, episode_ids):
        actual = context.read(episode_ids=episode_ids, metadata=metadata)
        expected = [self.expected_episode]
        assert actual == expected

    @pytest.mark.parametrize(
        "episode_nums",
        [1, [1]],
    )
    def test_read_by_nums(self, context, metadata, episode_nums):
        actual = context.read(episode_nums=episode_nums, metadata=metadata)
        expected = [self.expected_episode]
        assert actual == expected

    @pytest.mark.parametrize(
        "episode_titles",
        ["Episode 1", ["Episode 1"]],
    )
    def test_read_by_title(self, context, metadata, episode_titles):
        actual = context.read(episode_titles=episode_titles, metadata=metadata)
        expected = [self.expected_episode]
        assert actual == expected

    @pytest.mark.parametrize(
        "seasons",
        [1, [1]],
    )
    def test_read_by_seasons(self, context, metadata, seasons):
        actual = context.read(seasons=seasons, metadata=metadata)
        expected = self.expected_episode
        assert len(actual) == 3  # length of metadata for season 1
        assert actual[0] == expected

    def test_read_no_args(self, context):
        with pytest.raises(ValueError):
            context.read()

    def test_read_all(self, context, metadata):
        actual = context.read(get_all=True, metadata=metadata)
        expected = self.expected_episode
        assert len(actual) == 5  # length of metadata for all seasons
        assert actual[0] == expected


class TestGetScriptExtractor:
    def test_get_script_extractor_kaggle(self):
        """Test that _get_script_extractor returns KaggleScriptExtractor for 'kaggle' source."""
        extractor = _get_script_extractor("kaggle")
        assert isinstance(extractor, KaggleScriptExtractor)

    def test_get_script_extractor_invalid_source(self):
        """Test that _get_script_extractor raises ValueError for invalid source."""
        with pytest.raises(ValueError):
            _get_script_extractor("invalid_source")


class TestGetCreditExtractor:
    def test_get_credit_extractor_omdb(self):
        """Test that _get_credit_extractor returns OMDBCreditExtractor for 'omdb' source."""
        extractor = _get_credit_extractor("omdb", omdb_api_key="key")
        assert isinstance(extractor, OMDBCreditExtractor)

    def test_get_credit_extractor_invalid_source(self):
        """Test that _get_credit_extractor raises ValueError for invalid source."""
        with pytest.raises(ValueError):
            _get_credit_extractor("invalid_source")


class TestGetRatingExtractor:
    def test_get_rating_extractor_omdb(self):
        """Test that _get_rating_extractor returns OMDBRatingExtractor for 'omdb' source."""
        extractor = _get_rating_extractor("omdb", omdb_api_key="key")
        assert isinstance(extractor, OMDBRatingExtractor)

    def test_get_rating_extractor_invalid_source(self):
        """Test that _get_rating_extractor raises ValueError for invalid source."""
        with pytest.raises(ValueError):
            _get_rating_extractor("invalid_source")


class TestGetExporter:
    def test_get_exporter_database(self):
        """Test that _get_exporter returns DatabaseExporter for 'database' save type."""
        exporter = _get_exporter("database")
        assert isinstance(exporter, DatabaseExporter)

    def test_get_exporter_csv(self):
        """Test that _get_exporter returns CsvExporter for 'csv' save type."""
        exporter = _get_exporter("csv")
        assert isinstance(exporter, CsvExporter)

    def test_get_exporter_json(self):
        """Test that _get_exporter returns JsonExporter for 'json' save type."""
        exporter = _get_exporter("json")
        assert isinstance(exporter, JsonExporter)

    def test_get_exporter_invalid_save_type(self):
        """Test that _get_exporter raises ValueError for invalid save type."""
        with pytest.raises(ValueError):
            _get_exporter("invalid_type")


class TestReadEpisodes:
    def test_invalid_source(self):
        source = {"invalid_key": "value"}
        with pytest.raises(AssertionError):
            read_episodes(source=source)

    def test_invalid_script_extractor(self):
        """Test that read_episodes raises AssertionError for invalid script extractor."""
        source = {"script": "invalid_script"}
        with pytest.raises(AssertionError):
            read_episodes(source=source)

    def test_invalid_credit_extractor(self):
        """Test that read_episodes raises AssertionError for invalid credit extractor."""
        source = {"credit": "invalid_credit"}
        with pytest.raises(AssertionError):
            read_episodes(source=source)

    def test_invalid_rating_extractor(self):
        """Test that read_episodes raises AssertionError for invalid rating extractor."""
        source = {"rating": "invalid_rating"}
        with pytest.raises(AssertionError):
            read_episodes(source=source)

    def test_read_episode(
        self, metadata, monkeypatch, fake_script, fake_credit, fake_rating, fake_episode
    ):
        """Test reading single episode."""
        source = {"script": "kaggle", "credit": "omdb", "rating": "omdb"}

        monkeypatch.setattr(
            KaggleScriptExtractor,
            "extract",
            lambda self, *a, **k: fake_script,
        )
        monkeypatch.setattr(
            OMDBCreditExtractor,
            "extract",
            lambda self, *a, **k: fake_credit,
        )
        monkeypatch.setattr(
            OMDBRatingExtractor,
            "extract",
            lambda self, *a, **k: fake_rating,
        )

        actual = read_episodes(
            source=source,
            episode_ids=["S01E02"],
            omdb_api_key="key",
            metadata=metadata,
        )
        expected = [fake_episode]
        assert actual == expected

    def test_read_episodes(
        self, metadata, monkeypatch, fake_script, fake_credit, fake_rating, fake_episode
    ):
        """Test reading multiple episodes."""
        source = {"script": "kaggle", "credit": "omdb", "rating": "omdb"}

        monkeypatch.setattr(
            KaggleScriptExtractor,
            "extract",
            lambda self, *a, **k: fake_script,
        )
        monkeypatch.setattr(
            OMDBCreditExtractor,
            "extract",
            lambda self, *a, **k: fake_credit,
        )
        monkeypatch.setattr(
            OMDBRatingExtractor,
            "extract",
            lambda self, *a, **k: fake_rating,
        )

        actual = read_episodes(
            source=source,
            episode_ids=["S01E02", "S01E02"],
            omdb_api_key="key",
            metadata=metadata,
        )
        expected = [fake_episode, fake_episode]
        assert actual == expected

    def test_read_episodes_by_seasons(
        self, metadata, monkeypatch, fake_script, fake_credit, fake_rating
    ):
        """Test reading episodes by seasons."""
        source = {"script": "kaggle", "credit": "omdb", "rating": "omdb"}

        monkeypatch.setattr(
            KaggleScriptExtractor,
            "extract",
            lambda self, *a, **k: fake_script,
        )
        monkeypatch.setattr(
            OMDBCreditExtractor,
            "extract",
            lambda self, *a, **k: fake_credit,
        )
        monkeypatch.setattr(
            OMDBRatingExtractor,
            "extract",
            lambda self, *a, **k: fake_rating,
        )

        actual = read_episodes(
            source=source,
            seasons=[1],
            omdb_api_key="key",
            metadata=metadata,
        )
        assert len(actual) == 3  # length of metadata for season 1

    def test_read_episodes_all(self, metadata, monkeypatch, fake_script, fake_credit, fake_rating):
        """Test reading all episodes with get_all=True."""
        source = {"script": "kaggle", "credit": "omdb", "rating": "omdb"}

        monkeypatch.setattr(
            KaggleScriptExtractor,
            "extract",
            lambda self, *a, **k: fake_script,
        )
        monkeypatch.setattr(
            OMDBCreditExtractor,
            "extract",
            lambda self, *a, **k: fake_credit,
        )
        monkeypatch.setattr(
            OMDBRatingExtractor,
            "extract",
            lambda self, *a, **k: fake_rating,
        )

        actual = read_episodes(
            source=source,
            get_all=True,
            omdb_api_key="key",
            metadata=metadata,
        )
        assert len(actual) == 5  # length of metadata for all seasons

    def test_read_episodes_empty_source(self, metadata, monkeypatch):
        """Test reading episodes with empty source dict (uses empty extractors)."""

        source = {}

        monkeypatch.setattr(
            EmptyScriptExtractor,
            "extract",
            lambda *a, **k: TestContext.expected_script,
        )
        monkeypatch.setattr(
            EmptyCreditExtractor,
            "extract",
            lambda *a, **k: TestContext.expected_credit,
        )
        monkeypatch.setattr(
            EmptyRatingExtractor,
            "extract",
            lambda *a, **k: TestContext.expected_rating,
        )

        actual = read_episodes(
            source=source,
            episode_ids=["S01E02"],
            metadata=metadata,
        )
        expected = [TestContext.expected_episode]
        assert actual == expected

    def test_read_episodes_script_only(self, metadata, monkeypatch):
        """Test reading episodes with only script extractor."""
        source = {"script": "kaggle"}

        expected_script = TestContext.expected_script
        expected_credit = TestContext.expected_credit
        expected_rating = TestContext.expected_rating

        monkeypatch.setattr(
            KaggleScriptExtractor,
            "extract",
            lambda *a, **k: expected_script,
        )
        monkeypatch.setattr(
            EmptyCreditExtractor,
            "extract",
            lambda *a, **k: expected_credit,
        )
        monkeypatch.setattr(
            EmptyRatingExtractor,
            "extract",
            lambda *a, **k: expected_rating,
        )

        actual = read_episodes(
            source=source,
            episode_ids=["S01E02"],
            metadata=metadata,
        )
        expected = [TestContext.expected_episode]
        assert actual == expected

    def test_read_episodes_credit_only(self, metadata, monkeypatch):
        """Test reading episodes with only credit extractor."""
        source = {"credit": "omdb"}

        expected_script = TestContext.expected_script
        expected_credit = TestContext.expected_credit
        expected_rating = TestContext.expected_rating

        monkeypatch.setattr(
            EmptyScriptExtractor,
            "extract",
            lambda *a, **k: expected_script,
        )
        monkeypatch.setattr(
            OMDBCreditExtractor,
            "extract",
            lambda *a, **k: expected_credit,
        )
        monkeypatch.setattr(
            EmptyRatingExtractor,
            "extract",
            lambda *a, **k: expected_rating,
        )

        actual = read_episodes(
            source=source,
            episode_ids=["S01E02"],
            omdb_api_key="key",
            metadata=metadata,
        )
        expected = [TestContext.expected_episode]
        assert actual == expected

    def test_read_episodes_rating_only(self, metadata, monkeypatch):
        """Test reading episodes with only rating extractor."""
        source = {"rating": "omdb"}

        monkeypatch.setattr(
            EmptyScriptExtractor,
            "extract",
            lambda *a, **k: TestContext.expected_script,
        )
        monkeypatch.setattr(
            EmptyCreditExtractor,
            "extract",
            lambda *a, **k: TestContext.expected_credit,
        )
        monkeypatch.setattr(
            OMDBRatingExtractor,
            "extract",
            lambda *a, **k: TestContext.expected_rating,
        )

        actual = read_episodes(
            source=source,
            episode_ids=["S01E02"],
            omdb_api_key="key",
            metadata=metadata,
        )
        expected = [TestContext.expected_episode]
        assert actual == expected
