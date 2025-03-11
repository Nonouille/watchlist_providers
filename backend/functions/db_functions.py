import psycopg2
from psycopg2 import pool
import json
from datetime import datetime
import contextlib

connection_pool = None


def get_db_connection() -> psycopg2.extensions.connection:
    """
    Retourne une connexion depuis le pool.
    Initialise le pool si nécessaire.
    """
    global connection_pool
    if connection_pool is None:
        DB_HOST = "localhost"
        DB_NAME = "checklist"
        DB_USER = "postgres"
        DB_PASSWORD = "root"
        DB_PORT = 5432

        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,
            10,
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
        )
    return connection_pool.getconn()


def release_db_connection(connexion):
    """
    Replace la connexion dans le pool.
    """
    global connection_pool
    if connection_pool and connexion:
        connection_pool.putconn(connexion)


def get_connexion_and_cursor():
    """
    Retourne une connexion et un curseur associé.
    """
    connexion = get_db_connection()
    return connexion, connexion.cursor()


def db_operation(commit: bool = False):
    """
    Décorateur pour centraliser la gestion de la connexion,
    du curseur, des exceptions, et du commit/rollback.

    Si commit=True, le commit est réalisé après l'exécution.
    En cas d'exception, le rollback est effectué.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            conn, cursor = None, None
            try:
                conn, cursor = get_connexion_and_cursor()
                result = func(cursor, *args, **kwargs)
                if commit:
                    conn.commit()
                return result
            except Exception as e:
                print(f"Erreur dans {func.__name__}: {e}")
                if conn:
                    conn.rollback()
                return None
            finally:
                if conn:
                    release_db_connection(conn)

        return wrapper

    return decorator


####################################################################################################
# --- Fonctions métier utilisant le décorateur ---


@db_operation(commit=True)
def modify_last_research_user(cursor, user_ID: str):
    """
    Met à jour la date de dernière recherche pour l'utilisateur.
    """
    now = datetime.now()
    cursor.execute(
        'UPDATE "USER" SET last_research = %s WHERE user_id = %s', (now, user_ID)
    )


@db_operation(commit=True)
def modify_user_providers(cursor, user_ID: str, country_code: str, providers: list):
    """
    Met à jour les fournisseurs pour l'utilisateur et le pays donné.
    Ajoute les nouveaux fournisseurs et supprime ceux qui ne sont plus présents.
    """
    cursor.execute(
        'SELECT provider_name FROM "PROVIDER" WHERE user_id = %s AND country_code = %s',
        (user_ID, country_code),
    )
    current_providers = [row[0] for row in cursor.fetchall()]

    # Supprimer les fournisseurs absents de la nouvelle liste
    providers_to_remove = [p for p in current_providers if p not in providers]
    if providers_to_remove:
        placeholders = ",".join(["%s"] * len(providers_to_remove))
        cursor.execute(
            f'DELETE FROM "PROVIDER" WHERE user_id = %s AND country_code = %s AND provider_name IN ({placeholders})',
            (user_ID, country_code, *providers_to_remove),
        )

    # Ajouter les nouveaux fournisseurs
    providers_to_add = [p for p in providers if p not in current_providers]
    for provider in providers_to_add:
        cursor.execute(
            'INSERT INTO "PROVIDER" (user_ID, country_code, provider_name) VALUES (%s, %s, %s)',
            (user_ID, country_code, provider),
        )
    return 0


@db_operation(commit=True)
def modify_film(cursor, user_ID: str, country_code: str, films: list):
    """
    Met à jour la liste des films pour l'utilisateur et le pays donné.
    Insère, met à jour ou supprime les films selon les changements.
    """
    cursor.execute(
        'SELECT film_id, title, grade, providers, date FROM "FILM" WHERE user_ID = %s AND country_code = %s',
        (user_ID, country_code),
    )
    existing_films = cursor.fetchall()

    # Insertion et mise à jour
    for film in films:
        # Si le film n'existe pas dans la BDD, insertion
        if not any(film["title"] == row[1] for row in existing_films):
            cursor.execute(
                'INSERT INTO "FILM" (user_ID, country_code, film_id, title, grade, providers, date) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (
                    user_ID,
                    country_code,
                    film["id"],
                    film["title"],
                    film["note"],
                    json.dumps(film["providers"]),
                    film["date"],
                ),
            )
        else:
            # Mise à jour en cas de modification des données
            for row in existing_films:
                if row[1] == film["title"]:
                    current_grade = row[2]
                    current_providers = json.loads(row[3]) if row[3] else []
                    current_date = row[4]
                    if current_grade != film["note"] or current_date != film["date"] or sorted(
                        current_providers
                    ) != sorted(film["providers"]):
                        cursor.execute(
                            'UPDATE "FILM" SET grade = %s, date = %s, providers = %s WHERE user_ID = %s AND country_code = %s AND title = %s',
                            (
                                film["note"],
                                film["date"],
                                json.dumps(film["providers"]),
                                user_ID,
                                country_code,
                                film["title"],
                            ),
                        )
                    break

    # Suppression des films qui ne sont plus présents
    for row in existing_films:
        if not any(film["title"] == row[1] for film in films):
            cursor.execute(
                'DELETE FROM "FILM" WHERE user_ID = %s AND country_code = %s AND title = %s',
                (user_ID, country_code, row[1]),
            )
    return 0


@db_operation(commit=True)
def get_userID(cursor, username: str) -> str:
    """
    Récupère l'ID de l'utilisateur à partir du nom d'utilisateur.
    Si l'utilisateur n'existe pas, il est créé.
    """
    cursor.execute(
        'SELECT user_id FROM "USER" WHERE Letterboxd_username = %s', (username,)
    )
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        now = datetime.now()
        cursor.execute(
            'INSERT INTO "USER" (letterboxd_username, created_at, last_research) VALUES (%s, %s, %s) RETURNING user_id',
            (username, now, now),
        )
        return cursor.fetchone()[0]


@db_operation()
def get_user_last_research_date(cursor, user_ID: str) -> str:
    """
    Retourne la date de dernière recherche de l'utilisateur.
    """
    cursor.execute('SELECT last_research FROM "USER" WHERE user_id = %s', (user_ID,))
    result = cursor.fetchone()
    return result[0] if result else None


@db_operation()
def get_user_providers(cursor, user_ID: str, country_code: str) -> list:
    """
    Retourne la liste des fournisseurs pour l'utilisateur et le pays donné.
    """
    cursor.execute(
        'SELECT provider_name FROM "PROVIDER" WHERE user_id = %s AND country_code = %s',
        (user_ID, country_code),
    )
    return [row[0] for row in cursor.fetchall()]


@db_operation()
def get_user_results(cursor, user_ID: str, country_code: str) -> list:
    """
    Retourne la liste des films pour l'utilisateur et le pays donné.
    """
    cursor.execute(
        'SELECT film_ID, title, grade, providers, date FROM "FILM" WHERE user_ID = %s AND country_code = %s',
        (user_ID, country_code),
    )
    result = cursor.fetchall()
    films = []
    for row in result:
        films.append(
            {
                "id": row[0],
                "title": row[1],
                "note": row[2],
                "providers": json.loads(row[3]),
                "date": row[4],
            }
        )
    return films
