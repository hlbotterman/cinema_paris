"""Main application file."""

from typing import Dict

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def read_root() -> Dict[str, str]:
    """Handle the root endpoint of the API.

    This function returns a welcome message for the cinema
    scheduling application.

    Returns
    -------
    Dict[str, str]
        A dictionary containing a welcome message
        for users of the application.

    """
    return {
        "message": (
            "Bienvenue à l'application de programmation "
            "des cinémas indépendants parisiens !"
        )
    }
