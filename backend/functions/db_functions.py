import psycopg2
from psycopg2 import pool
import json
from datetime import datetime
import contextlib

connection_pool = None

def get_db_connection():
    """
    Get a connection from the connection pool
    """
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
    """
    Release the connection back to the connection pool
    """
    global connection_pool
    if connection_pool and conn:
        connection_pool.putconn(conn)

@contextlib.contextmanager
def db_connection():
    """
    Context manager for database connections
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        if conn:
            release_db_connection(conn)
            
def get_userID(username):
    """
    Get the user ID for the given username
    If not found, create a new user and return the user ID
    """
    with db_connection() as conn:
        try:        
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            # Query to check if the user has existing results for this country code
            cursor.execute(
                'SELECT user_id FROM "USER" WHERE Letterboxd_username = %s',
                (username,)
            ) 
            result = cursor.fetchone()
            # A user exists, return the user ID
            if result:
                user_ID = result[0]
                
            # A user doesn't exist, create a new user and return the user ID
            else:
                now = datetime.now()
                cursor.execute(
                    'INSERT INTO "USER" (letterboxd_username, created_at, last_research) VALUES (%s,%s,%s) RETURNING user_id',
                    (username,now,now)
                )
                user_ID = cursor.fetchone()[0]
                connection_pool.commit()
            return user_ID
        
        except Exception as e:
            print(f"Failed to retrieve the user ID: {e}")
            release_db_connection(connection_pool)
            return -1
    
def get_user_last_research_date(user_ID):
    """
    Get the last research date for the given user ID
    """
    with db_connection() as conn:
        try:        
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            # Query to check if the user has existing results for this country code
            cursor.execute(
                'SELECT last_research FROM "USER" WHERE user_id = %s',
                (user_ID,)
            )
            result = cursor.fetchone()
            # A user exists, return the user ID
            if result:
                last_research = result[0]
                return last_research
            else:
                return None
        
        except Exception as e:
            print(f"Failed to retrieve the last research date for the user: {e}")
            release_db_connection(connection_pool)
            return None
    
def get_user_providers(user_ID,country_code):
    """
    Get the providers for the given user ID and country
    """
    with db_connection() as conn:
        try:        
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            # Query to check if the user has existing results for this country code
            cursor.execute(
                'SELECT provider_name FROM "PROVIDER" WHERE user_id = %s AND country_code = %s',
                (user_ID,country_code)
            )
            providers = [row[0] for row in cursor.fetchall()]
            return providers
        
        except Exception as e:
            release_db_connection(connection_pool)
            return []

def get_user_results(user_ID,country_code):
    """
    Get the results for the given user ID and country
    """
    with db_connection() as conn:
        try:
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            # Query to check if the user has existing results for this country code
            cursor.execute(
                'SELECT film_ID, title, grade, providers, date FROM "FILM" WHERE user_ID = %s AND country_code = %s',
                (user_ID,country_code)
            )
            result = cursor.fetchall()
            # A user has existing results, return the film list
            if result:
                films = []
                for row in result:
                    films.append({
                        "id": row[0],
                        "title": row[1],
                        "grade": row[2],
                        "providers": json.loads(row[3]),
                        "date": row[4]
                    })
                return films
            
            # A user doesn't have existing results, return an empty list
            else:
                return []
        
        except Exception as e:
            print(f"Failed to retrieve the user results: {e}")
            release_db_connection(connection_pool)
            return []

def modify_last_research_user(user_ID):
    """
    Update the last research date for the given user ID
    """
    with db_connection() as conn:
        try:
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            # Query to update the last research date for the user
            now = datetime.now()
            cursor.execute(
                'UPDATE "USER" SET last_research = %s WHERE user_id = %s',
                (now,user_ID)
            )
            connection_pool.commit()
            
        except Exception as e:
            print(f"Failed to update the last research date for the user: {e}")
            release_db_connection(connection_pool)
            return -1

def modify_user_providers(user_ID,country_code,providers):
    """
    Update the providers for the given user ID and country.
    If provider is not found, insert it.
    If provider is not in the new list, delete it.
    """
    with db_connection() as conn:
        try:
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            # Get current providers for this user and country
            cursor.execute(
                'SELECT provider_name FROM "PROVIDER" WHERE user_id = %s AND country_code = %s',
                (user_ID, country_code)
            )
            current_providers = [row[0] for row in cursor.fetchall()]
            
            # Delete providers that are in the database but not in the new list
            providers_to_remove = [p for p in current_providers if p not in providers]
            if providers_to_remove:
                placeholders = ','.join(['%s'] * len(providers_to_remove))
                cursor.execute(
                f'DELETE FROM "PROVIDER" WHERE user_id = %s AND country_code = %s AND provider_name IN ({placeholders})',
                (user_ID, country_code, *providers_to_remove)
                )
            
            # Add new providers that aren't already in the database
            providers_to_add = [p for p in providers if p not in current_providers]
            for provider in providers_to_add:
                cursor.execute(
                'INSERT INTO "PROVIDER" (user_ID, country_code, provider_name) VALUES (%s, %s, %s)',
                (user_ID, country_code, provider)
                )
            
            connection_pool.commit()
            return 0
            
        except Exception as e:
            print(f"Failed to update the user providers: {e}")
            release_db_connection(connection_pool)
            return -1

def modify_film(user_ID,country_code,films):
    """
    Update the film list for the given user ID and country.
    If film is not found, insert it.
    If film providers or grade have changed, update them.
    If film is not in the new list, delete it.
    """
    with db_connection() as conn:
        try:
            connection_pool = get_db_connection()
            cursor = connection_pool.cursor()
            #Query to get the films for the actual user_ID and country_code
            cursor.execute(
                'SELECT film_id, title, grade, providers, date FROM "FILM" WHERE user_ID = %s AND country_code = %s',
                (user_ID,country_code)
            )
            result = cursor.fetchall()
            print("Movies in DB", result)
            print("Movies in API", films)
            
            #Compare the films in the database with the new films
            for film in films:
                if film not in result:
                    #Insert the new film in the database
                    # Insert new film into the database
                    cursor.execute(
                        'INSERT INTO "FILM" (user_ID, country_code, film_id, title, grade, providers, date) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (user_ID, country_code, film["id"], film["title"], film["note"], json.dumps(film["providers"]), film.get("date", None))
                    )
                else:
                    for row in result:
                        if row[1] == film["title"]:  # Match by title
                            current_grade = row[2]
                            current_providers = json.loads(row[3]) if row[3] else []
                            
                            # Only update if data has changed
                            if current_grade != film["note"] or sorted(current_providers) != sorted(film["providers"]):
                                cursor.execute(
                                    'UPDATE "FILM" SET grade = %s, providers = %s WHERE user_ID = %s AND country_code = %s AND title = %s',
                                    (film["note"], json.dumps(film["providers"]), user_ID, country_code, film["title"])
                                )
                            break
                    
            #Delete the films in the database that are not in the new films
            for row in result:
                if row not in films:
                    cursor.execute(
                        'DELETE FROM "FILM" WHERE user_ID = %s AND country_code = %s AND title = %s',
                        (user_ID, country_code, row[1])
                    )
                    
            connection_pool.commit()
            return 0
            
            
        except Exception as e:
            print(f"Failed to update the film: {e}")
            release_db_connection(connection_pool)
            return -1
