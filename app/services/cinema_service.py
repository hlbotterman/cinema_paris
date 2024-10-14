"""Services for the cinema app."""

from datetime import datetime
from typing import Any, Dict

from app.core.cinema_config import CINEMAS
from app.models.models import Theater

cinemas = {
    cinema_id: cinema_info["name"]
    for cinema_id, cinema_info in CINEMAS.items()
}

theaters = [
    Theater(name=str(name), internal_id=str(id), location=None)
    for id, name in cinemas.items()
]


async def get_all_showtimes(date: datetime):
    """Get showtimes from all theaters for a given date.

    Parameters
    ----------
    date : datetime
        Date to get showtimes for.

    Returns
    -------
    list
        The showtimes for the given date.

    """
    showtimes = []
    for theater in theaters:
        showtimes.extend(await theater.get_showtimes(date))

    data: Dict[str, Dict[str, Any]] = {}
    for showtime in showtimes:
        movie = showtime.movie
        theater = showtime.theater
        if movie.title not in data:
            data[movie.title] = {
                "title": movie.title,
                "duree": movie.runtime,
                "genres": ", ".join(movie.genres),
                "casting": ", ".join(movie.cast),
                "realisateur": movie.director,
                "synopsis": movie.synopsis,
                "affiche": movie.affiche,
                "director": movie.director,
                "wantToSee": movie.wantToSee,
                "url": f"https://www.allocine.fr/film/fichefilm_gen_cfilm={movie.id}.html",
                "seances": {},
            }
        if theater.name not in data[movie.title]["seances"]:
            data[movie.title]["seances"][theater.name] = []
        data[movie.title]["seances"][theater.name].append(
            showtime.start_at.strftime("%H:%M")
        )

    return sorted(data.values(), key=lambda x: x["wantToSee"], reverse=True)


def translate_day(weekday: int) -> str:
    """Translate weekday number to french short weekday name.

    Parameters
    ----------
    weekday : int
        Weekday number.

    Returns
    -------
    str
        French short weekday name.

    """
    return {
        0: "lun",
        1: "mar",
        2: "mer",
        3: "jeu",
        4: "ven",
        5: "sam",
        6: "dim",
    }.get(weekday, "???")


def translate_month(num: int) -> str:
    """Translate month number to french short month name.

    Parameters
    ----------
    num : int
        Month number.

    Returns
    -------
    str
        French short month name.

    """
    return {
        1: "janv",
        2: "févr",
        3: "mars",
        4: "avr",
        5: "mai",
        6: "juin",
        7: "juil",
        8: "août",
        9: "sept",
        10: "oct",
        11: "nov",
        12: "déc",
    }.get(num, "???")
