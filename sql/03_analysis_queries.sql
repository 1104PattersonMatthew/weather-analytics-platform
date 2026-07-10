-- 1. Highest recorded temperature per city

SELECT
    c.city_name,
    c.state,
    MAX(w.temperature_max_f) AS highest_temperature_f
FROM weather_records w
JOIN cities c
    ON w.city_id = c.city_id
GROUP BY
    c.city_name,
    c.state
ORDER BY highest_temperature_f DESC;


-- 2. Total monthly precipitation by city

SELECT
    c.city_name,
    c.state,
    DATE_TRUNC('month', w.weather_date)::DATE AS month,
    ROUND(SUM(w.precipitation_in), 3) AS total_precipitation_in
FROM weather_records w
JOIN cities c
    ON w.city_id = c.city_id
GROUP BY
    c.city_name,
    c.state,
    DATE_TRUNC('month', w.weather_date)
ORDER BY
    c.city_name,
    month;


-- 3. Windiest week of the year per city based on average max daily wind speed

WITH weekly_wind AS (
    SELECT
        c.city_name,
        c.state,
        DATE_TRUNC('week', w.weather_date)::DATE AS week_start,
        ROUND(AVG(w.wind_speed_max_mph), 2) AS avg_max_wind_speed_mph
    FROM weather_records w
    JOIN cities c
        ON w.city_id = c.city_id
    GROUP BY
        c.city_name,
        c.state,
        DATE_TRUNC('week', w.weather_date)
),
ranked_weeks AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY city_name, state
            ORDER BY avg_max_wind_speed_mph DESC
        ) AS wind_rank
    FROM weekly_wind
)
SELECT
    city_name,
    state,
    week_start,
    avg_max_wind_speed_mph
FROM ranked_weeks
WHERE wind_rank = 1
ORDER BY avg_max_wind_speed_mph DESC;


-- 4. Average rainfall by city

SELECT
    c.city_name,
    c.state,
    ROUND(AVG(w.precipitation_in), 3) AS avg_daily_precipitation_in,
    ROUND(SUM(w.precipitation_in), 3) AS total_precipitation_in
FROM weather_records w
JOIN cities c
    ON w.city_id = c.city_id
GROUP BY
    c.city_name,
    c.state
ORDER BY total_precipitation_in DESC;


-- 5. Frequency of extreme temperature days by city

SELECT
    c.city_name,
    c.state,
    COUNT(*) AS total_days,
    COUNT(*) FILTER (WHERE w.temperature_max_f >= 95) AS extreme_heat_days,
    COUNT(*) FILTER (WHERE w.temperature_min_f <= 32) AS freezing_days
FROM weather_records w
JOIN cities c
    ON w.city_id = c.city_id
GROUP BY
    c.city_name,
    c.state
ORDER BY extreme_heat_days DESC;


-- 6. Hottest month of the year per city based on average daily max temperature

WITH monthly_temperature AS (
    SELECT
        c.city_name,
        c.state,
        DATE_TRUNC('month', w.weather_date)::DATE AS month,
        ROUND(AVG(w.temperature_max_f), 2) AS avg_max_temperature_f
    FROM weather_records w
    JOIN cities c
        ON w.city_id = c.city_id
    GROUP BY
        c.city_name,
        c.state,
        DATE_TRUNC('month', w.weather_date)
),
ranked_months AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY city_name, state
            ORDER BY avg_max_temperature_f DESC
        ) AS temp_rank
    FROM monthly_temperature
)
SELECT
    city_name,
    state,
    month,
    avg_max_temperature_f
FROM ranked_months
WHERE temp_rank = 1
ORDER BY avg_max_temperature_f DESC;