"""Routes for the API."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates

from app.services.cinema_service import (
    get_all_showtimes,
    translate_day,
    translate_month,
)

from ..core.cinema_config import CINEMAS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", name="home")
async def home(request: Request, delta: int = 0) -> Response:
    """Render the home page with cinema showtimes for a specific day.

    Parameters
    ----------
    request : Request
        The HTTP request object.
    delta : int, optional
        The number of days from today to fetch showtimes.
        Accepted range is between 0 and 6. by default 0

    Returns
    -------
    Response
        The rendered HTML response containing the cinema schedule,
        movie details, and available showtimes.

    """
    if delta > 6:
        delta = 6
    if delta < 0:
        delta = 0

    dates = [
        {
            "jour": translate_day((datetime.today() + timedelta(i)).weekday()),
            "chiffre": (datetime.today() + timedelta(i)).day,
            "mois": translate_month((datetime.today() + timedelta(i)).month),
            "choisi": i == delta,
            "index": i,
        }
        for i in range(7)
    ]

    films = await get_all_showtimes(datetime.today() + timedelta(days=delta))

    cinemas = [
        {"coordinates": data["coordinates"], "description": data["name"]}
        for data in CINEMAS.values()
    ]

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "films": films,
            "dates": dates,
            "cinemas": cinemas,
        },
    )
