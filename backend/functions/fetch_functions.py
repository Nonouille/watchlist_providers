import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, expect
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Load environment variables from .env file
TMDB_TOKEN = os.getenv("TMDB_TOKEN")
if TMDB_TOKEN is None:
    print(
        "TMDB_TOKEN environment variable not set. Please set it in your .env file."
    )
# Set the headers for the requests
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_TOKEN}",
}

def get_watchlist(username: str) -> list:
    """
    Retrieve the watchlist of a Letterboxd user by running the letterboxd_scrapper Docker image.
    """
    with sync_playwright() as playwright:
        watchlist = []
        
        print(f"Scraping watchlist for user: {username}")
        
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Visit the user's watchlist page
        page.goto(f"https://letterboxd.com/{username}/watchlist/", timeout=60000)
        last_page = get_last_page_number(page)
        print(f"Found {last_page} page(s) for {username}'s watchlist")
        extract_films(page,watchlist)
        
        # Loop through the pages
        if last_page > 1:
            for i in range(2, last_page + 1):
                page.goto(f"https://letterboxd.com/{username}/watchlist/page/{i}")
                # Increase timeout to avoid rate limiting
                page.wait_for_timeout(1500)
                extract_films(page,watchlist)
        
        # Print results
        print(f"Total films collected: {len(watchlist)}")
        
        # Close the browser and context
        context.close()
        browser.close()
        
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


def extract_films(page, watchlist: list):
    page.wait_for_selector("ul.poster-list li.poster-container")
    
    # Get all film containers on the page
    film_containers = page.query_selector_all("ul.poster-list li.poster-container")
    
    for film in film_containers:
        try:
            # Extract film title from alt attribute
            poster_img = film.query_selector("div.film-poster img")
            if not poster_img:
                continue
                
            title = poster_img.get_attribute("alt")
            
            # Extract film slug and year
            poster_div = film.query_selector("div.film-poster")
            if not poster_div:
                continue
                
            film_slug = poster_div.get_attribute("data-film-slug")
            
            # Check if there's a year in the slug
            year = None
            if film_slug:
                parts = film_slug.split("-")
                if len(parts) > 0 and len(parts[-1]) == 4 and parts[-1].isdigit():
                    year = int(parts[-1])
            
            # Check if this film has been rated by owner
            owner_rating = film.get_attribute("data-owner-rating")
            rating = int(owner_rating) if owner_rating and owner_rating != "0" else None
            
            # Build film info
            film_info = {
                "title": title,
            }
            
            if year:
                film_info["year"] = year
                
            if rating:
                film_info["rating"] = rating
                
            # Add to watchlist
            watchlist.append(film_info)
            
        except Exception as e:
            print(f"Error extracting film: {e}")


def get_last_page_number(page):
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # Wait for pagination to load
        page.wait_for_selector("div.paginate-pages", timeout=10000)
        
        # Find the last paginate-page element
        last_paginate_item = page.query_selector("li.paginate-page:last-child a")
    
        # Extract the page number from the last element
        if last_paginate_item:
            try:
                page_text = last_paginate_item.inner_text()
                if page_text.isdigit():
                    return int(page_text)
            except:
                pass
    except:
        return 1