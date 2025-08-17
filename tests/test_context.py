import pytest
from seinpy.context import Context
from seinpy.schema import Episode, Script, Credit, Rating, EpisodeRef, ScriptLine, Actor


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
            episode_id="S01E01",
            episode_num=1,
            episode_title="Episode 1",
        ),
        script_lines=[
            ScriptLine(speaker="Jerry", dialogue="Jerry: Hi, I'm Jerry."),
            ScriptLine(speaker="George", dialogue="George: Hi, I'm George."),
            ScriptLine(speaker="Kramer", dialogue="Kramer: Hi, I'm Kramer."),
            ScriptLine(speaker="Elaine", dialogue="Elaine: Hi, I'm Elaine."),
        ],
    )

    expected_credit = Credit(
        ref=EpisodeRef(
            episode_id="S01E01",
            episode_num=1,
            episode_title="Episode 1",
        ),
        description="This is the pilot episode of Seinfeld.",
        date="1989-07-05",
        writer=["Jerry Seinfeld", "Larry David"],
        director=["Jerry Seinfeld", "Larry David"],
        actors=[
            Actor(name="Jerry Seinfeld", role="Jerry"),
            Actor(name="Jason Alexander", role="George"),
            Actor(name="Michael Richards", role="Kramer"),
            Actor(name="Julia Louis-Dreyfus", role="Elaine"),
        ],
    )

    expected_rating = Rating(
        ref=EpisodeRef(
            episode_id="S01E01",
            episode_num=1,
            episode_title="Episode 1",
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
        actual = context._get_episode(episode_id="S01E01")
        expected = self.expected_episode
        assert actual == expected

    def test_get_episode_empty(self, context):
        with pytest.raises(ValueError):
            context._get_episode()

    def test_get_episodes_by_ids(self, context):
        actual = context._get_episodes(episode_ids=["S01E01", "S01E01"])
        expected = [
            self.expected_episode,
            self.expected_episode,
        ]
        assert actual == expected

    def test_get_episodes_by_nums(self, context):
        actual = context._get_episodes(episode_nums=[1, 1])
        expected = [
            self.expected_episode,
            self.expected_episode,
        ]
        assert actual == expected

    def test_get_episodes_by_titles(self, context):
        actual = context._get_episodes(
            episode_titles=["Episode 1", "Episode 1"]
        )
        expected = [
            context._get_episode(episode_title="Episode 1"),
            context._get_episode(episode_title="Episode 1"),
        ]
        assert actual == expected

    def test_get_episodes_by_seasons(self, context, metadata):
        actual = context._get_episodes(seasons=[1], metadata=metadata)
        expected = [
            context._get_episode(episode_id="S01E01"),
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
