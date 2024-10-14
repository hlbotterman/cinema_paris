"""Tests for the cinema service."""

import asyncio
from datetime import datetime
from typing import List

import pytest

from app.models.models import Showtime
from app.services.cinema_service import (
    get_all_showtimes,
    translate_day,
    translate_month,
)


@pytest.mark.asyncio
async def test_retrieves_showtimes(mocker) -> None:
    """Test that the showtimes are retrieved correctly."""
    mock_theater = mocker.Mock()
    mock_showtime = mocker.Mock()
    mock_showtime.movie.title = "Movie A"
    mock_showtime.movie.runtime = 120
    mock_showtime.movie.genres = ["Action", "Adventure"]
    mock_showtime.movie.cast = ["Actor A", "Actor B"]
    mock_showtime.movie.director = "Director A"
    mock_showtime.movie.synopsis = "Synopsis A"
    mock_showtime.movie.affiche = "Affiche A"
    mock_showtime.movie.wantToSee = 100
    mock_showtime.movie.id = 123
    mock_showtime.theater.name = "Theater A"
    mock_showtime.start_at.strftime.return_value = "14:00"
    mock_theater.get_showtimes.return_value = [mock_showtime]

    future: asyncio.Future[List[Showtime]] = asyncio.Future()
    future.set_result([mock_showtime])
    mock_theater.get_showtimes.return_value = future

    mocker.patch("app.services.cinema_service.theaters", [mock_theater])

    result = await get_all_showtimes(datetime.now())

    assert len(result) == 1
    assert result[0]["title"] == "Movie A"
    assert result[0]["seances"]["Theater A"] == ["14:00"]


def test_translate_day() -> None:
    """Test the translation of a day."""
    assert translate_day(0) == "lun"
    assert translate_day(1) == "mar"
    assert translate_day(2) == "mer"
    assert translate_day(3) == "jeu"
    assert translate_day(4) == "ven"
    assert translate_day(5) == "sam"
    assert translate_day(6) == "dim"

    assert translate_day(7) == "???"
    assert translate_day(-1) == "???"


def test_translate_month() -> None:
    """Test the translation of a month."""
    assert translate_month(1) == "janv"
    assert translate_month(2) == "févr"
    assert translate_month(3) == "mars"
    assert translate_month(4) == "avr"
    assert translate_month(5) == "mai"
    assert translate_month(6) == "juin"
    assert translate_month(7) == "juil"
    assert translate_month(8) == "août"
    assert translate_month(9) == "sept"
    assert translate_month(10) == "oct"
    assert translate_month(11) == "nov"
    assert translate_month(12) == "déc"

    assert translate_month(0) == "???"
    assert translate_month(13) == "???"
