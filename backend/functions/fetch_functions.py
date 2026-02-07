import random
import time
import requests
from urllib.parse import quote
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from playwright.sync_api import Error as PlaywrightError
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

def _goto_with_retries(page, url: str, *, timeout_ms: int = 60000, max_attempts: int = 3) -> bool:
    """
    Navigate with retries to survive transient DNS/network failures.
    Returns True on success, False after exhausting attempts.
    """
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            return True
        except PlaywrightError as e:
            last_err = e
            # Backoff with jitter
            sleep_s = min(2 ** attempt, 10) + random.uniform(0.1, 0.8)
            print(f"⚠️ page.goto failed (attempt {attempt}/{max_attempts}) for {url}: {str(e)[:160]}", flush=True)
            time.sleep(sleep_s)
        except Exception as e:
            last_err = e
            sleep_s = min(2 ** attempt, 10) + random.uniform(0.1, 0.8)
            print(f"⚠️ Unexpected error during navigation (attempt {attempt}/{max_attempts}) for {url}: {str(e)[:160]}", flush=True)
            time.sleep(sleep_s)

    if last_err:
        print(f"❌ Giving up navigating to {url}: {last_err}", flush=True)
    return False

def get_watchlist(username: str) -> list:
    """
    Retrieve the watchlist of a Letterboxd user via Playwright scraping.
    This function is best-effort: it will return partial results if some pages fail.
    """
    watchlist: list[dict] = []
    print(f"Scraping watchlist for user: {username}", flush=True)

    ua = UserAgent()
    user_agent = ua.random

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
                '--user-agent=' + user_agent
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
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
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(60000)
        def _apply_zoom():
            try:
                page.evaluate("document.body.style.zoom = '50%'")
            except Exception:
                pass
        
        
        # Visit the user's watchlist page
        first_url = f"https://letterboxd.com/{username}/watchlist/"
        if not _goto_with_retries(page, first_url, timeout_ms=60000, max_attempts=3):
            context.close()
            browser.close()
            return watchlist
        _apply_zoom()

        extract_films(page, watchlist)

        # Paginate by clicking numbered links if present (2, 3, 4, ...)
        page_number = 2
        while True:
            try:
                # Ensure pagination is in view / loaded
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                link = page.get_by_role("link", name=str(page_number), exact=True)
                if link.count() == 0:
                    break
                try:
                    with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
                        link.first.click()
                except Exception:
                    # Some navigations are not detected; best-effort fallback
                    link.first.click()
                    page.wait_for_load_state("domcontentloaded", timeout=60000)
                _apply_zoom()
                # Small delay to reduce rate limiting / bot detection
                page.wait_for_timeout(1500)
                extract_films(page, watchlist)
                page_number += 1
            except Exception:
                break
        
        # Print results
        print(f"Total films collected: {len(watchlist)}", flush=True)
        
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
        
        # Wait for the page to be usable (networkidle is often flaky on modern sites)
        page.wait_for_load_state('domcontentloaded', timeout=60000)
        try:
            page.wait_for_load_state('load', timeout=30000)
        except Exception:
            # Best-effort; selectors below will be the real gate.
            pass
        
        # Selectors to cover multiple Letterboxd markups (react + classic posters)
        selectors_to_try = [
            # Modern posters
            "div.film-poster",
            # Older / alternative poster containers
            "ul.poster-list li.poster-container",
            ".poster-container",
            # React-ish markup (some pages/users)
            "li.griditem div.react-component[data-item-name]",
            "li.griditem div.react-component",
            "div.react-component[data-item-name]",
            "div.react-component[data-film-id]",
            "li.griditem",
        ]
        
        element_found = False
        selected_selector = None
        
        # Scroll down gradually to trigger lazy loading
        for i in range(3):
            page.evaluate(f"window.scrollTo(0, {(i + 1) * 500})")
            time.sleep(1)
        
        # Try each selector quickly (don't burn minutes per page)
        for selector in selectors_to_try:
            try:
                page.wait_for_selector(selector, timeout=6000)
                element_found = True
                selected_selector = selector
                break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {str(e)[:140]}...", flush=True)
                continue
        
        if not element_found:
            # Helpful diagnostics: often a block page or an error page.
            try:
                title = page.title()
            except Exception:
                title = ""
            try:
                snippet = page.content()[:800].lower()
            except Exception:
                snippet = ""
            if any(k in snippet for k in ["cloudflare", "captcha", "attention required", "access denied", "forbidden"]):
                print(f"❌ Page appears blocked (title={title!r}).", flush=True)
            else:
                print(f"❌ Could not find any film containers (title={title!r}).", flush=True)
            return
        
        # Extract films using the successful selector
        film_elements = page.query_selector_all(selected_selector)
        existing = {(f.get("title"), f.get("date")) for f in watchlist if isinstance(f, dict)}
        
        # Process each element
        for i, element in enumerate(film_elements):
            try:
                film_info = extract_film_info_from_react_component(element)
                if film_info:
                    key = (film_info.get("title"), film_info.get("date"))
                    if key not in existing:
                        existing.add(key)
                        watchlist.append(film_info)
                else:
                    print(f"  ❌ Failed to extract info from element {i+1}", flush=True)
            except Exception as e:
                print(f"❌ Error processing film element {i+1}: {e}", flush=True)
                continue
        print(f"Extracted {len(film_elements)} films in page {page.url.split('/')[-2] if page.url.split('/')[-3] == 'page' else 1}", flush=True)

    except Exception as e:
        print(f"💥 Critical error in extract_films: {e}", flush=True)
        return

def extract_film_info_from_react_component(element):
    """Extract film information from various Letterboxd element shapes."""
    try:
        # 1) Fast path: film-poster markup (most common)
        film_name = element.get_attribute("data-film-name")
        if film_name:
            year = element.get_attribute("data-film-release-year")
            film_info = {"title": film_name}
            if year and str(year).isdigit():
                film_info["date"] = int(year)
            return film_info

        # Sometimes the container holds the film-poster div
        poster = element.query_selector("div.film-poster")
        if poster:
            film_name = poster.get_attribute("data-film-name")
            if film_name:
                year = poster.get_attribute("data-film-release-year")
                film_info = {"title": film_name}
                if year and str(year).isdigit():
                    film_info["date"] = int(year)
                return film_info

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
            # Last resort: some poster markup exposes title in the image alt
            img = element.query_selector("img[alt]")
            if img:
                alt = img.get_attribute("alt")
                if alt:
                    return {"title": alt}
            print("    ❌ No known film markup found in element")
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
        print(f"    ❌ Error extracting from React component: {e}", flush=True)
        return None


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
