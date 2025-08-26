import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TMDB_TOKEN = os.getenv("TMDB_TOKEN")
if TMDB_TOKEN is None:
    print(
        "TMDB_TOKEN environment variable not set. Please set it in your .env file or container environment."
        "TMDB_TOKEN environment variable not set. Please set it in your .env file or container environment."
    )

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
        
        ua = UserAgent()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--user-agent=' + ua.random
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=ua.random,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # Add stealth script to hide automation
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Remove automation indicators
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
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
                page.wait_for_timeout(2000)
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
    genres = get_genres_id()
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
            watchlist[index]["genres"] = [genres[genre_id] for genre_id in data["results"][0]["genre_ids"] if genre_id in genres]
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
    """
    Extract films from a Letterboxd watchlist page with enhanced detection evasion.
    """
    try:
        # Simulate human behavior
        time.sleep(random.uniform(2, 5))

        # Navigate like a human - scroll gradually
        page.evaluate("""
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        """)
        time.sleep(2)
        
        # Wait for the page to be fully loaded
        page.wait_for_load_state('domcontentloaded', timeout=30000)
        page.wait_for_load_state('networkidle', timeout=30000)
        
        # Updated selectors based on your HTML structure
        selectors_to_try = [
            'li.griditem div.react-component[data-item-name]',  # Most specific - targets the exact structure
            'li.griditem div.react-component',                 # Less specific but still good
            'div.react-component[data-item-name]',             # In case the li.griditem changes
            'div.react-component[data-film-id]',               # Alternative data attribute
            'li.griditem',                                     # Fallback to just the list items
            "ul.poster-list li.poster-container",              # Original selectors as fallback
            ".poster-container"
        ]
        
        element_found = False
        selected_selector = None
        
        # Scroll down gradually to trigger lazy loading
        for i in range(3):
            page.evaluate(f"window.scrollTo(0, {(i + 1) * 500})")
            time.sleep(1)
        
        # Try each selector with patience
        for selector in selectors_to_try:
            try:
                page.wait_for_selector(selector, timeout=15000)
                element_found = True
                selected_selector = selector
                break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {str(e)[:100]}...")
                continue
        
        if not element_found:
            print("❌ Could not find any film containers")
            return
        
        # Extract films using the successful selector
        film_elements = page.query_selector_all(selected_selector)
        
        # Process each element
        for i, element in enumerate(film_elements):
            try:
                film_info = extract_film_info_from_react_component(element)
                if film_info:
                    watchlist.append(film_info)
                else:
                    print(f"  ❌ Failed to extract info from element {i+1}")
            except Exception as e:
                print(f"❌ Error processing film element {i+1}: {e}")
                continue
        print(f"Extracted {len(film_elements)} films in page {page.url.split('/')[-2] if page.url.split('/')[-3] == 'page' else 1}")

    except Exception as e:
        print(f"💥 Critical error in extract_films: {e}")
        return

def extract_film_info_from_react_component(element):
    """Extract film information from a React component element"""
    try:
        # First, try to find the react component div within the element
        react_component = element.query_selector('div.react-component[data-item-name]')
        if not react_component:
            # If the element itself is the react component
            if element.get_attribute('data-item-name'):
                react_component = element
            else:
                # Try to find any react component within
                react_component = element.query_selector('div.react-component')
        
        if not react_component:
            print("    ❌ No react component found in element")
            return None
        
        # Extract data from React component attributes
        item_name = react_component.get_attribute("data-item-name")
        
        # If we have item_name, use that as the title
        if item_name:
            title = item_name
            # Extract year from title if present (e.g., "Philadelphia (1993)")
            year = None
            if "(" in title and ")" in title:
                try:
                    year_part = title.split("(")[-1].split(")")[0]
                    if year_part.isdigit() and len(year_part) == 4:
                        year = int(year_part)
                        # Clean title by removing the year part
                        title = title.split("(")[0].strip()
                except:
                    pass
            
            film_info = {"title": title}
            if year:
                film_info["date"] = year
                
            return film_info
        
    except Exception as e:
        print(f"    ❌ Error extracting from React component: {e}")
        return None


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
    
def get_genres_id() -> dict:
    """
    Retrieve the genres from The Movie Database API.
    """
    response = requests.get(
        "https://api.themoviedb.org/3/genre/movie/list?language=en-US", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve the genres. HTTP Status Code: {response.status_code}"
        )
    data = response.json()
    genres = {}
    for genre in data["genres"]:
        genres[genre["id"]] = genre["name"]
    return genres