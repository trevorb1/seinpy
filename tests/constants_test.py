"""Tests for the constants and enumerations in seinpy."""

from seinpy import CreditSource, ExporterType, RatingSource, ScriptSource, Source
from seinpy.constants import (
    CREDIT_EXTRACTORS,
    EXPORTERS,
    RATING_EXTRACTORS,
    SCRIPT_EXTRACTORS,
)
from seinpy.context import (
    _get_credit_extractor,
    _get_exporter,
    _get_rating_extractor,
    _get_script_extractor,
)
from seinpy.credits.omdb import OMDBCreditExtractor
from seinpy.exporters.json import JsonExporter
from seinpy.ratings.omdb import OMDBRatingExtractor
from seinpy.scripts.kaggle import KaggleScriptExtractor
from seinpy.utils import is_valid_extractors


class TestScriptSource:
    """Tests for the ScriptSource enumeration."""

    def test_script_source_members(self) -> None:
        """Test all members and their string values."""
        expected = {
            "KAGGLE": "kaggle",
            "IMDB": "imdb",
            "SEINFELDSCRIPTS": "seinfeldscripts",
            "SEINOLOGY": "seinology",
        }
        for name, value in expected.items():
            member = getattr(ScriptSource, name)
            assert member == value
            assert isinstance(member, str)

    def test_script_source_in_script_extractors(self) -> None:
        """Test that all members are present in SCRIPT_EXTRACTORS."""
        for member in ScriptSource:
            assert member in SCRIPT_EXTRACTORS
            assert member.value in SCRIPT_EXTRACTORS

    def test_script_source_extractor_dispatch(self) -> None:
        """Test that _get_script_extractor works with enum members."""
        extractor = _get_script_extractor(ScriptSource.KAGGLE)
        assert isinstance(extractor, KaggleScriptExtractor)


class TestCreditSource:
    """Tests for the CreditSource enumeration."""

    def test_credit_source_members(self) -> None:
        """Test all members and their string values."""
        expected = {
            "OMDB": "omdb",
            "ROTTENTOMATOES": "rottentomatoes",
        }
        for name, value in expected.items():
            member = getattr(CreditSource, name)
            assert member == value
            assert isinstance(member, str)

    def test_credit_source_in_credit_extractors(self) -> None:
        """Test that all members are present in CREDIT_EXTRACTORS."""
        for member in CreditSource:
            assert member in CREDIT_EXTRACTORS
            assert member.value in CREDIT_EXTRACTORS

    def test_credit_source_extractor_dispatch(self) -> None:
        """Test that _get_credit_extractor works with enum members."""
        extractor = _get_credit_extractor(CreditSource.OMDB, omdb_api_key="key")
        assert isinstance(extractor, OMDBCreditExtractor)


class TestRatingSource:
    """Tests for the RatingSource enumeration."""

    def test_rating_source_members(self) -> None:
        """Test all members and their string values."""
        expected = {
            "OMDB": "omdb",
            "ROTTENTOMATOES": "rottentomatoes",
        }
        for name, value in expected.items():
            member = getattr(RatingSource, name)
            assert member == value
            assert isinstance(member, str)

    def test_rating_source_in_rating_extractors(self) -> None:
        """Test that all members are present in RATING_EXTRACTORS."""
        for member in RatingSource:
            assert member in RATING_EXTRACTORS
            assert member.value in RATING_EXTRACTORS

    def test_rating_source_extractor_dispatch(self) -> None:
        """Test that _get_rating_extractor works with enum members."""
        extractor = _get_rating_extractor(RatingSource.OMDB, omdb_api_key="key")
        assert isinstance(extractor, OMDBRatingExtractor)


class TestExporterType:
    """Tests for the ExporterType enumeration."""

    def test_exporter_type_members(self) -> None:
        """Test all members and their string values."""
        expected = {
            "DATABASE": "database",
            "CSV": "csv",
            "JSON": "json",
        }
        for name, value in expected.items():
            member = getattr(ExporterType, name)
            assert member == value
            assert isinstance(member, str)

    def test_exporter_type_in_exporters(self) -> None:
        """Test that all members are present in EXPORTERS."""
        for member in ExporterType:
            assert member in EXPORTERS
            assert member.value in EXPORTERS

    def test_exporter_dispatch(self) -> None:
        """Test that _get_exporter works with enum members."""
        exporter = _get_exporter(ExporterType.JSON)
        assert isinstance(exporter, JsonExporter)


class TestSourceWithEnums:
    """Tests for using Source with enum instances."""

    def test_source_initialization_with_enums(self) -> None:
        """Test instantiating Source using enum members."""
        source = Source(
            script=ScriptSource.KAGGLE,
            credit=CreditSource.OMDB,
            rating=RatingSource.OMDB,
        )
        assert source.script == "kaggle"
        assert source.credit == "omdb"
        assert source.rating == "omdb"
        assert is_valid_extractors(source) is True
