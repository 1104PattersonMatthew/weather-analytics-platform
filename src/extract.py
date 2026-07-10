import csv
import json
from pathlib import Path

import requests


API_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"


def get_project_root():
    return Path(__file__).resolve().parents[1]


def load_cities():
    project_root = get_project_root()
    cities_path = project_root / "config" / "cities.csv"

    cities = []

    with open(cities_path, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["latitude"] = float(row["latitude"])
            row["longitude"] = float(row["longitude"])
            cities.append(row)

    return cities


def fetch_weather_data(city):
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto",
    }

    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()

    return response.json()


def save_raw_json(data, city):
    project_root = get_project_root()
    output_folder = project_root / "data" / "raw"
    output_folder.mkdir(parents=True, exist_ok=True)

    file_name = f"{city['slug']}_weather_2024.json"
    output_path = output_folder / file_name

    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Saved raw data for {city['city_name']} to {output_path}")


def main():
    cities = load_cities()

    for city in cities:
        weather_data = fetch_weather_data(city)
        save_raw_json(weather_data, city)

    print("Extraction complete.")


if __name__ == "__main__":
    main()