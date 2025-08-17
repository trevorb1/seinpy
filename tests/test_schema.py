import pytest
from seinpy.schema import ScriptLine, Actor, EpisodeRef, Script, Rating, Credit, Episode


@pytest.fixture
def episode_ref():
    return EpisodeRef(episode_id="S01E01", episode_num=1, episode_title="Episode 1")


class TestScriptLine:
    def test_script_line_capitalize(self):
        script_line = ScriptLine(speaker="jerry", dialogue="Hello Newman")
        assert script_line.speaker == "Jerry"

    def test_script_line_capitalize_with_spaces(self):
        script_line = ScriptLine(speaker="  jerry  ", dialogue="Hello Newman")
        assert script_line.speaker == "Jerry"

    def test_script_line_capitalize_multiple_words(self):
        script_line = ScriptLine(speaker="jerry seinfeld", dialogue="Hello Newman")
        assert script_line.speaker == "Jerry Seinfeld"


class TestActor:
    def test_actor_capitalize(self):
        actor = Actor(name="jerry", role="Jerry")
        assert actor.name == "Jerry"

    def test_actor_capitalize_with_spaces(self):
        actor = Actor(name="  jerry  ", role="Jerry")
        assert actor.name == "Jerry"

    def test_actor_capitalize_multiple_words(self):
        actor = Actor(name="jerry seinfeld", role="Jerry")
        assert actor.name == "Jerry Seinfeld"


class TestEpisodeRef:
    def test_equality(self):
        episode_ref = EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title="Episode 1"
        )
        assert episode_ref == episode_ref
        assert episode_ref != EpisodeRef(
            episode_id="S01E02", episode_num=1, episode_title="Episode 1"
        )
        assert episode_ref != EpisodeRef(
            episode_id="S01E01", episode_num=2, episode_title="Episode 1"
        )
        assert episode_ref != EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title="Episode 2"
        )
        assert episode_ref != EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title=None
        )

    def test_true_false(self):
        episode_ref = EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title="Episode 1"
        )
        assert bool(episode_ref)

    def test_episode_title_validation(self, episode_ref):
        assert episode_ref.episode_title == "Episode 1."

    def test_episode_title_validation_with_spaces(self):
        ref = EpisodeRef(
            episode_id="S01E01",
            episode_num=1,
            episode_title="  episode   number,   one   (1)  ",
        )
        assert ref.episode_title == "Episode Number, One (1)."

    def test_episode_title_validation_with_period(self):
        ref = EpisodeRef(episode_id="S01E01", episode_num=1, episode_title="Episode 1.")
        assert ref.episode_title == "Episode 1."

    def test_episode_title_validation_with_exclamation(self):
        ref = EpisodeRef(episode_id="S01E01", episode_num=1, episode_title="Episode 1!")
        assert ref.episode_title == "Episode 1!"

    def test_episode_title_validation_with_question(self):
        ref = EpisodeRef(episode_id="S01E01", episode_num=1, episode_title="Episode 1?")
        assert ref.episode_title == "Episode 1?"

    def test_episode_title_validation_none(self):
        ref = EpisodeRef(episode_id="S01E01", episode_num=1, episode_title=None)
        assert not ref.episode_title

    def test_episode_title_validation_invalid_type(self):
        with pytest.raises(ValueError):
            EpisodeRef(episode_id="S01E01", episode_num=1, episode_title=123)

    def test_episode_id_validation(self):
        ref = EpisodeRef(episode_id="s01e01", episode_num=1, episode_title="Test")
        assert ref.episode_id == "S01E01"

    def test_episode_id_validation_with_spaces(self):
        ref = EpisodeRef(episode_id="  s01e01  ", episode_num=1, episode_title="Test")
        assert ref.episode_id == "S01E01"

    def test_episode_id_validation_invalid_format(self):
        with pytest.raises(ValueError):
            EpisodeRef(episode_id="S1E1", episode_num=1, episode_title="Test")


class TestRating:
    def test_rating_num_votes_validation(self, episode_ref):
        rating = Rating(
            ref=episode_ref, rating=4.5, num_votes=100, link="https://example.com"
        )
        assert rating.num_votes == 100

    def test_rating_num_votes_validation_none(self, episode_ref):
        rating = Rating(
            ref=episode_ref, rating=4.5, num_votes=None, link="https://example.com"
        )
        assert rating.num_votes == 0

    def test_rating_validation_none(self, episode_ref):
        rating = Rating(
            ref=episode_ref, rating=None, num_votes=100, link="https://example.com"
        )
        assert rating.rating == 0

    def test_rating_validation_out_of_range_max(self, episode_ref):
        with pytest.raises(ValueError, match="rating must be between 0 and 100"):
            Rating(
                ref=episode_ref, rating=101, num_votes=100, link="https://example.com"
            )

    def test_rating_validation_out_of_range_min(self, episode_ref):
        with pytest.raises(ValueError, match="rating must be between 0 and 100"):
            Rating(
                ref=episode_ref, rating=-1, num_votes=100, link="https://example.com"
            )

    def test_link_validation_none(self, episode_ref):
        rating = Rating(ref=episode_ref, rating=75.5, num_votes=100, link=None)
        assert rating.link == ""

    def test_link_validation_empty(self, episode_ref):
        rating = Rating(ref=episode_ref, rating=75.5, num_votes=100, link="")
        assert rating.link == ""

    def test_link_validation_invalid_url(self, episode_ref):
        with pytest.raises(ValueError):
            Rating(ref=episode_ref, rating=75.5, num_votes=100, link="invalid_url")


class TestEpisode:
    def test_validate_metadata_matching_refs(self):
        ref = EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title="Test Episode."
        )
        episode = Episode(
            script=Script(ref=ref, script_lines=[]),
            rating=Rating(ref=ref, rating=75.5, num_votes=100),
            credit=Credit(ref=ref),
        )
        assert episode._validate_metadata() == episode

    def test_validate_metadata_mismatched_refs(self):
        script_ref = EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title="Test Episode."
        )
        rating_ref = EpisodeRef(
            episode_id="S01E02", episode_num=2, episode_title="Different Episode."
        )

        with pytest.raises(ValueError):
            Episode(
                script=Script(ref=script_ref, script_lines=[]),
                rating=Rating(ref=rating_ref, rating=75.5, num_votes=100),
            )

    def test_validate_metadata_partial_components(self):
        ref = EpisodeRef(
            episode_id="S01E01", episode_num=1, episode_title="Test Episode."
        )
        episode = Episode(
            script=Script(ref=ref, script_lines=[]),
            rating=Rating(ref=ref, rating=75.5, num_votes=100),
        )
        assert episode._validate_metadata() == episode

    def test_validate_metadata_no_components(self):
        episode = Episode()
        assert episode._validate_metadata() == episode
