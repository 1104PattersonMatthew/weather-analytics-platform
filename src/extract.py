import json
from pathlib import Path

#for http request
import requests


API_URL = "https://archive-api.open-meteo.com/v1/archive"

#test city
CITY = {
    "name": "Reno",
    "state": "NV",
    "country": "USA",
    "latitude": 39.5296,
    "longitude": -119.8138
}

#for however long we want the data to be
START_DATE = "2024-01-01"
END_DATE = "2024-01-07"

#parameters for what api needs
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
        "timezone": "auto"
    }

    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def save_raw_json(data, city):
    project_root = Path(__file__).resolve().parents[1]
    output_folder = project_root / "data" / "raw"
    output_folder.mkdir(parents=True, exist_ok=True)

    file_name = f"{city['name'].lower()}_weather_sample.json"
    output_path = output_folder / file_name

    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Saved raw weather data to {output_path}")


def main():
    weather_data = fetch_weather_data(CITY)
    save_raw_json(weather_data, CITY)


if __name__ == "__main__":
    main()