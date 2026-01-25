CREATE TABLE "USER" (
    user_id SERIAL PRIMARY KEY,
    letterboxd_username VARCHAR,
    created_at TIMESTAMP,
    last_research TIMESTAMP
);
CREATE TABLE "PROVIDER"(
    provider_name VARCHAR,
    country_code VARCHAR,
    user_id INT,
    PRIMARY KEY (user_id, country_code, provider_name),
    FOREIGN KEY (user_id) REFERENCES "USER"(user_id)
);
CREATE TABLE "FILM"(
    film_id INT,
    title VARCHAR,
    grade FLOAT,
    providers VARCHAR,
    date INT,
    country_code VARCHAR,
    genres VARCHAR,
    user_id INT,
    PRIMARY KEY (user_id, country_code, film_id),
    FOREIGN KEY (user_id) REFERENCES "USER"(user_id)
);