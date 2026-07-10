CREATE TABLE IF NOT EXISTS cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    UNIQUE (city_name, state, country)
);

CREATE TABLE IF NOT EXISTS weather_records (
    record_id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL,
    weather_date DATE NOT NULL,
    temperature_max_f NUMERIC(6, 2),
    temperature_min_f NUMERIC(6, 2),
    precipitation_in NUMERIC(8, 3),
    wind_speed_max_mph NUMERIC(8, 2),

    CONSTRAINT fk_weather_city
        FOREIGN KEY (city_id)
        REFERENCES cities(city_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_city_weather_date
        UNIQUE (city_id, weather_date),

    CONSTRAINT valid_temperature_order
        CHECK (
            temperature_max_f IS NULL
            OR temperature_min_f IS NULL
            OR temperature_max_f >= temperature_min_f
        ),

    CONSTRAINT non_negative_precipitation
        CHECK (precipitation_in IS NULL OR precipitation_in >= 0),

    CONSTRAINT non_negative_wind_speed
        CHECK (wind_speed_max_mph IS NULL OR wind_speed_max_mph >= 0)
);