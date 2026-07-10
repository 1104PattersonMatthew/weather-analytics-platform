-- dml template used by src/load.py.
-- the actual values are passed safely from Python using parameterized queries.
-- avoids hardcoding data directly into SQL and helps prevent SQL injection risks.

INSERT INTO cities (
    city_name,
    state,
    country,
    latitude,
    longitude
)
VALUES (
    %s, %s, %s, %s, %s
)
ON CONFLICT (city_name, state, country)
DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude
RETURNING city_id;


INSERT INTO weather_records (
    city_id,
    weather_date,
    temperature_max_f,
    temperature_min_f,
    precipitation_in,
    wind_speed_max_mph
)
VALUES (
    %s, %s, %s, %s, %s, %s
)
ON CONFLICT (city_id, weather_date)
DO UPDATE SET
    temperature_max_f = EXCLUDED.temperature_max_f,
    temperature_min_f = EXCLUDED.temperature_min_f,
    precipitation_in = EXCLUDED.precipitation_in,
    wind_speed_max_mph = EXCLUDED.wind_speed_max_mph;