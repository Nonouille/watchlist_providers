import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import inquirer
import os
from flask import Flask, render_template,request, send_from_directory
import psycopg2
from psycopg2 import pool

app = Flask(__name__)

connection_pool = None

def get_db_connection():
    global connection_pool
    
    # Initialize the connection pool if it doesn't exist
    if connection_pool is None:
        DB_HOST="localhost"
        DB_NAME="checklist"
        DB_USER="postgres"
        DB_PASSWORD="root"
        DB_PORT=5432
        
        # Create a connection pool with min 1, max 10 connections
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
    
    # Get a connection from the pool
    return connection_pool.getconn()

def release_db_connection(conn):
    global connection_pool
    if connection_pool:
        connection_pool.putconn(conn)
    

def get_watchlist(username):
    watchlist = []
    page = 1
    
    while True:
        url = f'https://letterboxd.com/{username}/watchlist/page/{page}/'
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve watchlist for user {username}. HTTP Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        films = soup.find_all('li', class_='poster-container')

        if not films:
            break
        
        for film in films:
            title = film.find('img')['alt']
            infos = film.find('div', class_='film-poster')['data-film-slug']
            if len(infos.split('-')[-1]) == 4 and infos.split('-')[-1].isnumeric() and title[-4:] != infos.split('-')[-1]:
                date = int(infos.split('-')[-1])
                watchlist.append({'title': title, 'date': date})
            else:
                watchlist.append({'title': title})
        
        page += 1
    
    return watchlist

def get_ids(watchlist):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzUwMDE0OGU5ODYxMGFjNjI4ZTc3N2QxMTgwZDQxNyIsIm5iZiI6MTczNzU1NTg1Mi40OTcsInN1YiI6IjY3OTBmZjhjYmE0Njk5MGY1NGRmZjZhZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oUTZhoCrugczQbR02PA2h-ZGOpSjR5EIS9IL6nva63E"
    }
    indexed_watchlist = []
    for index,film in enumerate(watchlist):
        title_url_compatible = quote(film["title"])
        if 'date' in film:
            response = requests.get(f'https://api.themoviedb.org/3/search/movie?query={title_url_compatible}&primary_release_year={film["date"]}', headers=headers)
        else:
            response = requests.get(f'https://api.themoviedb.org/3/search/movie?query={title_url_compatible}', headers=headers)
            
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve the film id for '{film}'. HTTP Status Code: {response.status_code}")
        
        data = response.json()
        if data['results']:
            watchlist[index]['id'] = data['results'][0]['id']
            watchlist[index]['note'] = round(data['results'][0]['vote_average'], 1)
            indexed_watchlist.append(watchlist[index])
        indexed_watchlist.sort(key=lambda x: x.get('note', 0), reverse=True)
        
    return indexed_watchlist
   
def get_providers(watchlist):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzUwMDE0OGU5ODYxMGFjNjI4ZTc3N2QxMTgwZDQxNyIsIm5iZiI6MTczNzU1NTg1Mi40OTcsInN1YiI6IjY3OTBmZjhjYmE0Njk5MGY1NGRmZjZhZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oUTZhoCrugczQbR02PA2h-ZGOpSjR5EIS9IL6nva63E"
    }
    for index,film in enumerate(watchlist):
        id = int(film["id"])
        response = requests.get(f'https://api.themoviedb.org/3/movie/{id}/watch/providers', headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve the film providers for '{film}'. HTTP Status Code: {response.status_code}")
        
        providers = []
        data = response.json()
        if "results" in data and 'FR' in data["results"] and 'flatrate' in data["results"]['FR']:
            flatrate = data["results"]['FR']['flatrate']
            for provider in flatrate:
                providers.append(provider['provider_name'])
        watchlist[index]['providers'] = providers
        
    return [film for film in watchlist if film["providers"]]

def sort_watchlist(watchlist,providers):
    sorted_watchlist = []
    for film in watchlist:
        new_providers = [provider for provider in film["providers"] if provider in providers]
        if new_providers:
            film["providers"] = new_providers
            sorted_watchlist.append(film)
    return sorted_watchlist

def shorten_providers(watchlist):
    for index, film in enumerate(watchlist):
        providers = film["providers"]
        known_providers = []
        for provider in providers:
            main_name = provider.split()[0]
            if (main_name not in known_providers) and (main_name[:-1] not in known_providers) and (main_name + '+' not in known_providers):
                known_providers.append(main_name)
        watchlist[index]["providers"] = known_providers
    return watchlist

def your_providers(region_providers):
    question = "Which streaming platform can you access? (SPACE to select | ENTER to valid)"
    list_of_options = region_providers
    questions = [
        inquirer.Checkbox('providers',
                          message=question,
                          choices=list_of_options,
                          ),
    ]
    answers = inquirer.prompt(questions)
    return answers['providers']
 
def region_providers(country_code):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzUwMDE0OGU5ODYxMGFjNjI4ZTc3N2QxMTgwZDQxNyIsIm5iZiI6MTczNzU1NTg1Mi40OTcsInN1YiI6IjY3OTBmZjhjYmE0Njk5MGY1NGRmZjZhZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oUTZhoCrugczQbR02PA2h-ZGOpSjR5EIS9IL6nva63E"
    }

    response = requests.get(f"https://api.themoviedb.org/3/watch/providers/movie?watch_region={country_code}", headers=headers)
    if response.status_code != 200 :
        raise Exception(f"Impossible to retrieve the movie streaming platform for your region : {country_code}")

    region_providers = []
    data = response.json()
    if data["results"]:
        response_providers = data["results"]
        for response_provider in response_providers:
            if "display_priorities" in response_provider and country_code in response_provider["display_priorities"]:
                region_providers.append(response_provider["provider_name"])
                
    return region_providers

def get_regions():
    url = "https://api.themoviedb.org/3/watch/providers/regions?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzUwMDE0OGU5ODYxMGFjNjI4ZTc3N2QxMTgwZDQxNyIsIm5iZiI6MTczNzU1NTg1Mi40OTcsInN1YiI6IjY3OTBmZjhjYmE0Njk5MGY1NGRmZjZhZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oUTZhoCrugczQbR02PA2h-ZGOpSjR5EIS9IL6nva63E"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the regions. HTTP Status Code: {response.status_code}")
    data = response.json()
    regions = []
    for region in data["results"]:
        regions.append(region["iso_3166_1"])
    return regions

regions_list = get_regions()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        country_code = request.form['country_code']
        region_providers_list = region_providers(country_code)
        return render_template('index.html', username=username, country_code=country_code, region_providers=region_providers_list, regions=regions_list)
    return render_template('index.html', regions=regions_list)

@app.route('/results', methods=['POST'])
def results():
    username = request.form['username']
    country_code = request.form['country_code']
    selected_providers = request.form.getlist('providers')

    watchlist = get_watchlist(username)
    watchlist = get_ids(watchlist)
    watchlist = get_providers(watchlist)
    watchlist = sort_watchlist(watchlist, selected_providers)

    return render_template('results.html', watchlist=watchlist)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=True)
