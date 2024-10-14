"""Tests for models.

Classes:
    TestMovie: Tests for the Movie model.
    TestShowtime: Tests for the Showtime model.
    TestTheater: Tests for the Theater model.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from app.models.models import Movie, Showtime, Theater


class TestMovie:
    """Tests for the Movie model."""

    def test_movie_model_valid_data(self) -> None:
        """Test the Movie model with valid data."""
        valid_data = {
            "title": "Inception",
            "runtime": 148,
            "genres": ["Sci-Fi", "Action"],
            "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            "director": "Christopher Nolan",
            "synopsis": "A fake synopsis...",
            "affiche": "url/to/affiche.jpg",
            "wantToSee": 1200,
            "id": 1,
        }
        movie = Movie.model_validate(valid_data)
        assert movie.title == "Inception"
        assert movie.runtime == 148
        assert movie.genres == ["Sci-Fi", "Action"]
        assert movie.director == "Christopher Nolan"

    def test_movie_model_invalid_data(self) -> None:
        """Test the Movie model with invalid data."""
        invalid_data = {
            "runtime": 148,
            "genres": ["Sci-Fi", "Action"],
            "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            "director": "Christopher Nolan",
            "synopsis": "A fake synopsis...",
            "affiche": "url/to/affiche.jpg",
            "wantToSee": 1200,
            "id": 1,
        }

        with pytest.raises(ValueError):
            Movie.model_validate(invalid_data)


class TestShowtime:
    """Tests for the Showtime model."""

    def test_showtime_models_with_valid_objects(self) -> None:
        """Test the Showtime model with valid objects."""
        mock_movie = Movie(
            title="Test Movie",
            runtime=120,
            genres=["Action", "Thriller"],
            cast=["Actor 1", "Actor 2"],
            director="Test Director",
            synopsis="Test synopsis",
            affiche="http://example.com/image.jpg",
            wantToSee=500,
            id=1,
        )
        mock_theater = Theater(
            name="Test Theater", internal_id="T001", location="Test Location"
        )
        mock_start_time = datetime.now()

        showtime = Showtime(
            movie=mock_movie, theater=mock_theater, start_at=mock_start_time
        )

        assert showtime.movie == mock_movie
        assert showtime.theater == mock_theater
        assert showtime.start_at == mock_start_time

    def test_showtime_models_with_invvalid_objects(self) -> None:
        """Test the Showtime model with invvalid objects."""
        mock_movie = Movie(
            title="Test Movie",
            runtime=120,
            genres=["Action", "Thriller"],
            cast=["Actor 1", "Actor 2"],
            director="Test Director",
            synopsis="Test synopsis",
            affiche="http://example.com/image.jpg",
            wantToSee=500,
            id=1,
        )
        mock_theater = Theater(
            name="Test Theater", internal_id="T001", location="Test Location"
        )
        mock_start_at = datetime.now()

        with pytest.raises(ValidationError):
            Showtime.model_validate(
                {"movie": mock_movie, "theater": mock_theater}
            )
        with pytest.raises(ValidationError):
            Showtime.model_validate(
                {"movie": mock_movie, "start_at": mock_start_at}
            )
        with pytest.raises(ValidationError):
            Showtime.model_validate(
                {"theater": mock_theater, "start_at": mock_start_at}
            )


class TestTheater:
    """Tests for the Theater model."""

    def test_create_theater_with_valid_data(self) -> None:
        """Test creating a Theater with valid data."""
        theater = Theater(
            name="Test Theater", internal_id="T001", location="Test Location"
        )
        assert theater.name == "Test Theater"
        assert theater.internal_id == "T001"
        assert theater.location == "Test Location"

    def test_create_theater_with_invalid_data(self) -> None:
        """Test creating a Theater with an invalid data."""
        with pytest.raises(ValidationError):
            Theater.model_validate({"name": "name", "location": "location"})
        with pytest.raises(ValidationError):
            Theater.model_validate(
                {"internal_id": "internal_id", "location": "location"}
            )
        with pytest.raises(ValidationError):
            Theater.model_validate(
                {"name": "name", "internal_id": "internal_id"}
            )

    @pytest.mark.asyncio
    async def test_get_showtimes(self, mocker: MockerFixture) -> None:
        """Test the get_showtimes method."""
        mock_fetch = mocker.patch.object(Theater, "fetch_showtimes_page")
        mock_parse_movie = mocker.patch.object(Theater, "parse_movie")
        mock_parse_movie.side_effect = lambda movie_data: Movie(
            title=movie_data["title"],
            runtime=120,
            genres=[],
            cast=[],
            director="Test Director",
            synopsis="Test Synopsis",
            affiche="",
            wantToSee=0,
            id=1,
        )

        mock_data_page1 = {
            "results": [
                {
                    "movie": {"id": "123", "title": "Test Movie"},
                    "showtimes": {
                        "dubbed": [{"startsAt": "2023-05-01T10:00:00"}],
                        "original": [{"startsAt": "2023-05-01T12:00:00"}],
                        "local": [{"startsAt": "2023-05-01T14:00:00"}],
                    },
                }
            ],
            "pagination": {"page": "1", "totalPages": "2"},
        }

        mock_data_page2 = {
            "results": [
                {
                    "movie": {"id": "456", "title": "Another Movie"},
                    "showtimes": {
                        "dubbed": [{"startsAt": "2023-05-01T16:00:00"}],
                        "original": [],
                        "local": [],
                    },
                }
            ],
            "pagination": {"page": "2", "totalPages": "2"},
        }

        mock_fetch.side_effect = [mock_data_page1, mock_data_page2]

        expected_times = [
            datetime(2023, 5, 1, 10, 0),
            datetime(2023, 5, 1, 12, 0),
            datetime(2023, 5, 1, 14, 0),
            datetime(2023, 5, 1, 16, 0),
        ]

        theater = Theater(
            name="Test Theater", internal_id="12345", location="Test Location"
        )
        date = datetime(2023, 5, 1)
        showtimes = await theater.get_showtimes(date)

        assert len(showtimes) == 4
        assert all(isinstance(showtime, Showtime) for showtime in showtimes)
        assert showtimes[0].movie.title == "Test Movie"
        assert showtimes[3].movie.title == "Another Movie"
        assert [showtime.start_at for showtime in showtimes] == expected_times
        assert mock_fetch.call_count == 2
        mock_fetch.assert_has_calls(
            [mocker.call(date, 1), mocker.call(date, 2)]
        )

    @pytest.mark.asyncio
    async def test_get_showtimes_no_results(
        self, mocker: MockerFixture
    ) -> None:
        """Test the get_showtimes method with no results."""
        mock_fetch = mocker.patch.object(Theater, "fetch_showtimes_page")
        mock_fetch.return_value = {"message": "no.showtime.error"}

        theater = Theater(
            name="Test Theater", internal_id="T001", location="Test Location"
        )
        date = datetime(2023, 5, 1)
        showtimes = await theater.get_showtimes(date)

        assert len(showtimes) == 0
        assert mock_fetch.call_count == 1
        mock_fetch.assert_called_once_with(date, 1)

    def test_parse_runtime_hours_and_minutes(self) -> None:
        """Test parsing runtime hours and minutes."""
        assert Theater._parse_runtime("1h 54min") == 114

    def test_parse_runtime_only_hours(self) -> None:
        """Test parsing runtime hours only."""
        assert Theater._parse_runtime("2h") == 120

    def test_parse_runtime_only_minutes(self) -> None:
        """Test parsing runtime minutes only."""
        assert Theater._parse_runtime("45min") == 45

    def test_parse_runtime_no_time(self) -> None:
        """Test parsing runtime with no time."""
        assert Theater._parse_runtime("") == 0

    def test_parse_runtime_invalid_format(self) -> None:
        """Test parsing runtime with invalid format."""
        assert Theater._parse_runtime("invalid") == 0
