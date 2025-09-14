import pytest
from seinpy.context import Context
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


@pytest.fixture
def context(dummy_script_extractor, dummy_credit_extractor, dummy_rating_extractor):
    return Context(
        script_extractor=dummy_script_extractor,
        credit_extractor=dummy_credit_extractor,
        rating_extractor=dummy_rating_extractor,
    )


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
