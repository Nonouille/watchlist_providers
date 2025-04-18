import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Load environment variables from .env file
TMDB_TOKEN = os.getenv("TMDB_TOKEN")
if TMDB_TOKEN is None:
    raise ValueError(
        "TMDB_TOKEN environment variable not set. Please set it in your .env file."
    )
# Set the headers for the requests
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_TOKEN}",
}

def get_watchlist(username: str) -> list:
    """
    Retrieve the watchlist of a Letterboxd user.
    """
    watchlist = []
    page = 1

    while True:
        url = f"https://letterboxd.com/{username}/watchlist/page/{page}/"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve watchlist for user {username}. HTTP Status Code: {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")
        films = soup.find_all("li", class_="poster-container")

        if not films:
            break

        for film in films:
            title = film.find("img")["alt"]
            infos = film.find("div", class_="film-poster")["data-film-slug"]
            if (
                len(infos.split("-")[-1]) == 4
                and infos.split("-")[-1].isnumeric()
                and title[-4:] != infos.split("-")[-1]
            ):
                date = int(infos.split("-")[-1])
                watchlist.append({"title": title, "date": date})
            else:
                watchlist.append({"title": title})

        page += 1

    return watchlist


def get_ids(watchlist: list) -> list:
    """
    Retrieve the film id and note from The Movie Database API.
    """
    indexed_watchlist = []
    for index, film in enumerate(watchlist):
        title_url_compatible = quote(film["title"])
        if "date" in film:
            response = requests.get(
                f'https://api.themoviedb.org/3/search/movie?query={title_url_compatible}&primary_release_year={film["date"]}',
                headers=headers,
            )
        else:
            response = requests.get(
                f"https://api.themoviedb.org/3/search/movie?query={title_url_compatible}",
                headers=headers,
            )

        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve the film id for '{film}'. HTTP Status Code: {response.status_code}"
            )

        data = response.json()
        if data["results"]:
            watchlist[index]["id"] = data["results"][0]["id"]
            watchlist[index]["note"] = round(data["results"][0]["vote_average"], 1)
            watchlist[index]["date"] = data["results"][0]["release_date"].split("-")[0]
            indexed_watchlist.append(watchlist[index])
        indexed_watchlist.sort(key=lambda x: x.get("note", 0), reverse=True)

    return indexed_watchlist


def get_providers(watchlist: list) -> list:
    """
    Retrieve the film providers from The Movie Database API.
    """
    for index, film in enumerate(watchlist):
        id = int(film["id"])
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{id}/watch/providers", headers=headers
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve the film providers for '{film}'. HTTP Status Code: {response.status_code}"
            )

        providers = []
        data = response.json()
        if (
            "results" in data
            and "FR" in data["results"]
            and "flatrate" in data["results"]["FR"]
        ):
            flatrate = data["results"]["FR"]["flatrate"]
            for provider in flatrate:
                providers.append(provider["provider_name"])
        watchlist[index]["providers"] = providers

    return [film for film in watchlist if film["providers"]]


def sort_watchlist(watchlist: list, providers: list) -> list:
    """
    Sort the watchlist by providers.
    """
    sorted_watchlist = []
    for film in watchlist:
        new_providers = [
            provider for provider in film["providers"] if provider in providers
        ]
        if new_providers:
            film["providers"] = new_providers
            sorted_watchlist.append(film)
    return sorted_watchlist


def get_region_providers(country_code: str) -> list:
    """
    Retrieve the movie streaming platform for a specific region.
    """
    response = requests.get(
        f"https://api.themoviedb.org/3/watch/providers/movie?watch_region={country_code}",
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"Impossible to retrieve the movie streaming platform for your region : {country_code}"
        )

    region_providers = []
    data = response.json()
    if data["results"]:
        response_providers = data["results"]
        for response_provider in response_providers:
            if (
                "display_priorities" in response_provider
                and country_code in response_provider["display_priorities"]
            ):
                region_providers.append(response_provider["provider_name"])

    return region_providers


def get_all_regions() -> list:
    """
    Retrieve all regions from The Movie Database API.
    """
    response = requests.get(
        "https://api.themoviedb.org/3/watch/providers/regions?language=en-US",
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve the regions. HTTP Status Code: {response.status_code}"
        )
    data = response.json()
    regions = []
    for region in data["results"]:
        regions.append(region["iso_3166_1"])
    return regions
