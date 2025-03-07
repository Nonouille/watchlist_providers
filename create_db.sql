\c checklist;

CREATE TABLE "USER" (
    user_id SERIAL PRIMARY KEY,
    letterboxd_username VARCHAR,
    created_at TIMESTAMP,
    last_research TIMESTAMP
);
CREATE TABLE "PROVIDER"(
    provider_name VARCHAR PRIMARY KEY,
    country_code VARCHAR,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES "USER"(user_id)
);
CREATE TABLE "FILM"(
    film_id INT PRIMARY KEY,
    title VARCHAR,
    grade FLOAT,
    providers VARCHAR,
    date INT,
    country_code VARCHAR,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES "USER"(user_id)
);