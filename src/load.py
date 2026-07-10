import os
from pathlib import Path

import warnings

warnings.filterwarnings(
    "ignore",
    message="Signature.*numpy.longdouble.*",
    category=UserWarning
)

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import execute_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_project_root():
    return Path(__file__).resolve().parents[1]


def load_environment():
    project_root = get_project_root()
    load_dotenv(project_root / ".env")

    required_variables = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]

    missing_variables = [
        variable for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise EnvironmentError(
            f"Missing required environment variables: {missing_variables}"
        )


def get_connection(database_name=None):
    db_name = database_name or os.getenv("DB_NAME")

    return psycopg2.connect(
        dbname=db_name,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def create_database_if_not_exists():
    target_database = os.getenv("DB_NAME")

    connection = get_connection(database_name="postgres")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s;",
                (target_database,)
            )

            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(target_database)
                    )
                )
                print(f"Created database: {target_database}")
            else:
                print(f"Database already exists: {target_database}")

    finally:
        connection.close()


def create_schema(connection):
    project_root = get_project_root()
    schema_path = project_root / "sql" / "01_schema.sql"

    with open(schema_path, "r") as file:
        schema_sql = file.read()

    with connection.cursor() as cursor:
        cursor.execute(schema_sql)

    connection.commit()
    print("Schema created or already exists.")


def clean_number(value):
    if pd.isna(value):
        return None

    return float(value)


def load_cleaned_data(connection):
    project_root = get_project_root()
    cleaned_path = project_root / "data" / "cleaned" / "weather_cleaned.csv"

    if not cleaned_path.exists():
        raise FileNotFoundError(
            "Cleaned CSV not found. Run python src/profile_clean.py first."
        )

    df = pd.read_csv(cleaned_path)
    df["weather_date"] = pd.to_datetime(df["weather_date"]).dt.date

    city_id_lookup = {}

    unique_cities = df[
        ["city_name", "state", "country", "latitude", "longitude"]
    ].drop_duplicates()

    with connection.cursor() as cursor:
        for _, city in unique_cities.iterrows():
            cursor.execute(
                """
                INSERT INTO cities (
                    city_name,
                    state,
                    country,
                    latitude,
                    longitude
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (city_name, state, country)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
                RETURNING city_id;
                """,
                (
                    city["city_name"],
                    city["state"],
                    city["country"],
                    clean_number(city["latitude"]),
                    clean_number(city["longitude"]),
                )
            )

            city_id = cursor.fetchone()[0]
            city_key = (city["city_name"], city["state"], city["country"])
            city_id_lookup[city_key] = city_id

        weather_rows = []

        for _, row in df.iterrows():
            city_key = (row["city_name"], row["state"], row["country"])
            city_id = city_id_lookup[city_key]

            weather_rows.append((
                city_id,
                row["weather_date"],
                clean_number(row["temperature_max_f"]),
                clean_number(row["temperature_min_f"]),
                clean_number(row["precipitation_in"]),
                clean_number(row["wind_speed_max_mph"]),
            ))

        execute_values(
            cursor,
            """
            INSERT INTO weather_records (
                city_id,
                weather_date,
                temperature_max_f,
                temperature_min_f,
                precipitation_in,
                wind_speed_max_mph
            )
            VALUES %s
            ON CONFLICT (city_id, weather_date)
            DO UPDATE SET
                temperature_max_f = EXCLUDED.temperature_max_f,
                temperature_min_f = EXCLUDED.temperature_min_f,
                precipitation_in = EXCLUDED.precipitation_in,
                wind_speed_max_mph = EXCLUDED.wind_speed_max_mph;
            """,
            weather_rows
        )

    connection.commit()
    print(f"Loaded {len(unique_cities)} cities.")
    print(f"Loaded or updated {len(weather_rows)} weather records.")


def main():
    load_environment()
    create_database_if_not_exists()

    connection = get_connection()

    try:
        create_schema(connection)
        load_cleaned_data(connection)
    finally:
        connection.close()

    print("Database load complete.")


if __name__ == "__main__":
    main()