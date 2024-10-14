"""Classes for the cinema_paris app."""

import base64
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class Movie(BaseModel):
    """Model for a movie."""

    title: str
    runtime: int
    genres: List[str]
    cast: List[str]
    director: str
    synopsis: str
    affiche: str
    wantToSee: int
    id: int


class Showtime(BaseModel):
    """Model for a Showtime."""

    movie: Movie
    theater: "Theater"
    start_at: datetime


class Theater(BaseModel):
    """Model for a theater."""

    name: str
    internal_id: str
    location: Optional[str]

    async def fetch_showtimes_page(
        self, date: datetime, page: int
    ) -> Dict[str, Any]:
        """Fetch showtimes data for a specific page from the Allociné API.

        Parameters
        ----------
        date : datetime
            The date for which to fetch showtimes.
        page : int
            The page number to retrieve (to handle pagination of results).

        Returns
        -------
        dict
            A dictionary containing the showtimes data in JSON format.

        """
        datestr = date.strftime("%Y-%m-%d")
        url = f"https://www.allocine.fr/_/showtimes/theater-{self.internal_id}/d-{datestr}/p-{page}/"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise Exception(
                    f"Error: {response.status_code} - {response.text}"
                )
            return response.json()

    async def get_showtimes(self, date: datetime) -> List[Showtime]:
        """Retrieve showtimes for a given date.

        Parameters
        ----------
        date : datetime
            The date for which to retrieve showtimes.

        Returns
        -------
        List[Showtime]
            A list of Showtime objects representing
            the showtimes for the given date.

        """
        showtimes = []
        page = 1

        while True:
            data = await self.fetch_showtimes_page(date, page)

            if data.get("message") in [
                "no.showtime.error",
                "next.showtime.on",
            ] or data.get("error"):
                break

            # Parsing movie data
            for movie_data in data["results"]:
                movie = self.parse_movie(movie_data["movie"])
                showtime_list = (
                    movie_data["showtimes"].get("dubbed", [])
                    + movie_data["showtimes"].get("original", [])
                    + movie_data["showtimes"].get("local", [])
                )

                for showtime_data in showtime_list:
                    start_time = datetime.strptime(
                        showtime_data["startsAt"], "%Y-%m-%dT%H:%M:%S"
                    )
                    showtimes.append(
                        Showtime(
                            movie=movie, theater=self, start_at=start_time
                        )
                    )

            # Stop if last page
            if int(data["pagination"]["page"]) >= int(
                data["pagination"]["totalPages"]
            ):
                break
            page += 1

        return showtimes

    def parse_movie(self, movie_info: Dict[str, Any]) -> Movie:
        """Parse movie information and return a Movie object.

        Parameters
        ----------
        movie_info : dict
            A dictionary containing information about the movie
            retrieved from the API.

        Returns
        -------
        Movie
            A Movie object with the structured information about the movie.

        """
        runtime = self._parse_runtime(movie_info.get("runtime", None))
        genres = [genre["translate"] for genre in movie_info.get("genres", [])]
        cast = self.parse_cast(movie_info.get("cast", {}).get("edges", []))
        director = self.parse_director(movie_info.get("credits", []))
        affiche_info = movie_info.get("poster")
        affiche = affiche_info.get("url", "") if affiche_info else ""
        want_to_see = int(movie_info.get("wantToSee", 0))

        movie_id = self.decode_movie_id(movie_info["id"])

        return Movie(
            title=movie_info["title"],
            runtime=runtime,
            genres=genres,
            cast=cast,
            director=director,
            synopsis=movie_info.get("synopsis", ""),
            affiche=affiche,
            wantToSee=want_to_see,
            id=movie_id,
        )

    def decode_movie_id(self, encoded_id: str) -> int:
        """Decode the movie ID encoded in base64.

        Parameters
        ----------
        encoded_id : str
            The movie ID encoded in base64 format.

        Returns
        -------
        int
            The movie ID as an integer.

        Raises
        ------
        Exception
            If the encoded ID is not valid or cannot be decoded.

        """
        try:
            decoded_id = (
                base64.b64decode(encoded_id).decode("utf-8").split(":")[-1]
            )
            return int(decoded_id)
        except (ValueError, TypeError):
            raise Exception(f"Invalid movie ID format: {encoded_id}")

    def parse_cast(self, edges: List[dict]) -> List[str]:
        """Parse the cast information and return a list of actors.

        Parameters
        ----------
        edges : List[dict]
            A list of dictionaries representing the cast of the movie.

        Returns
        -------
        List[str]
            A list of full names of the movie's actors.

        """
        cast = []
        for node_dict in edges:
            actor_info = node_dict.get("node", {}).get("actor", {})
            if actor_info:
                firstname = actor_info.get("firstName", " ")
                lastname = actor_info.get("lastName", " ")
                cast.append(
                    f"{firstname} {lastname}"
                    if firstname and lastname
                    else "Unknown"
                )
        return cast

    def parse_director(self, credits: List[dict]) -> str:
        """Parse the director's information from the movie's credits.

        Parameters
        ----------
        credits : List[dict]
            A list of dictionaries representing the movie credits,
            including information about the director.

        Returns
        -------
        str
            The full name of the director, or "Unknown" if not available.

        """
        if isinstance(credits, list) and credits:
            person = credits[0].get("person", {})
            first_name = person.get("firstName", "Unknown")
            last_name = person.get("lastName", "Unknown")
            return f"{first_name} {last_name}"
        return "Unknown"

    @staticmethod
    def _parse_runtime(runtime_str: str | None) -> int:
        """Parse runtime string and return minutes.

        Parameters
        ----------
        runtime_str : str | None
            runtime string in the format "Xh Ymin"

        Returns
        -------
        int
            runtime in minutes

        """
        if runtime_str is None:
            return 0
        hours, minutes = 0, 0
        if "h" in runtime_str:
            hours = int(runtime_str.split("h")[0])
        if "min" in runtime_str:
            minutes = int(runtime_str.split("min")[0].split()[-1])
        return hours * 60 + minutes
