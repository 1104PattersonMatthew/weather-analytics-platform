import json
from pathlib import Path

import warnings

warnings.filterwarnings(
    "ignore",
    message="Signature.*numpy.longdouble.*",
    category=UserWarning
)

import pandas as pd


def get_project_root():
    return Path(__file__).resolve().parents[1]


def load_city_config():
    project_root = get_project_root()
    cities_path = project_root / "config" / "cities.csv"
    return pd.read_csv(cities_path)


def flatten_city_weather(city):
    project_root = get_project_root()
    raw_path = project_root / "data" / "raw" / f"{city['slug']}_weather_2024.json"

    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw file: {raw_path}")

    with open(raw_path, "r") as file:
        raw_data = json.load(file)

    daily = raw_data["daily"]

    df = pd.DataFrame({
        "city_name": city["city_name"],
        "state": city["state"],
        "country": city["country"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "weather_date": daily["time"],
        "temperature_max_f": daily["temperature_2m_max"],
        "temperature_min_f": daily["temperature_2m_min"],
        "precipitation_in": daily["precipitation_sum"],
        "wind_speed_max_mph": daily["wind_speed_10m_max"],
    })

    return df


def profile_dataframe(df):
    profile = []

    profile.append("Weather Data Profile Report")
    profile.append("=" * 40)
    profile.append(f"Total rows: {len(df)}")
    profile.append(f"Total columns: {len(df.columns)}")
    profile.append("")

    profile.append("Columns and data types:")
    profile.append(str(df.dtypes))
    profile.append("")

    profile.append("Null values by column:")
    profile.append(str(df.isnull().sum()))
    profile.append("")

    duplicate_count = df.duplicated(subset=["city_name", "weather_date"]).sum()
    profile.append(f"Duplicate city/date records: {duplicate_count}")
    profile.append("")

    profile.append("Numeric summary:")
    profile.append(str(df.describe()))
    profile.append("")

    invalid_temp_order = df[df["temperature_max_f"] < df["temperature_min_f"]]
    negative_precip = df[df["precipitation_in"] < 0]
    negative_wind = df[df["wind_speed_max_mph"] < 0]
    unrealistic_temp = df[
        (df["temperature_max_f"] < -100) |
        (df["temperature_max_f"] > 150) |
        (df["temperature_min_f"] < -100) |
        (df["temperature_min_f"] > 150)
    ]

    profile.append("Unexpected value range checks:")
    profile.append(f"Rows where max temp is below min temp: {len(invalid_temp_order)}")
    profile.append(f"Rows with negative precipitation: {len(negative_precip)}")
    profile.append(f"Rows with negative wind speed: {len(negative_wind)}")
    profile.append(f"Rows with unrealistic temperatures: {len(unrealistic_temp)}")
    profile.append("")

    return "\n".join(profile)


def clean_dataframe(df):
    df = df.copy()

    df["weather_date"] = pd.to_datetime(df["weather_date"])

    numeric_columns = [
        "latitude",
        "longitude",
        "temperature_max_f",
        "temperature_min_f",
        "precipitation_in",
        "wind_speed_max_mph",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    text_columns = ["city_name", "state", "country"]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    df = df.drop_duplicates(subset=["city_name", "weather_date"])

    df = df[
        (df["temperature_max_f"] >= df["temperature_min_f"]) &
        (df["precipitation_in"] >= 0) &
        (df["wind_speed_max_mph"] >= 0)
    ]

    df = df.sort_values(by=["city_name", "weather_date"])

    return df


def main():
    project_root = get_project_root()
    cities_df = load_city_config()

    all_weather_data = []

    for _, city in cities_df.iterrows():
        city_weather_df = flatten_city_weather(city)
        all_weather_data.append(city_weather_df)

    combined_df = pd.concat(all_weather_data, ignore_index=True)

    profile_report = profile_dataframe(combined_df)

    reports_folder = project_root / "reports"
    reports_folder.mkdir(parents=True, exist_ok=True)

    profile_path = reports_folder / "data_profile_report.txt"

    with open(profile_path, "w") as file:
        file.write(profile_report)

    cleaned_df = clean_dataframe(combined_df)

    cleaned_folder = project_root / "data" / "cleaned"
    cleaned_folder.mkdir(parents=True, exist_ok=True)

    cleaned_path = cleaned_folder / "weather_cleaned.csv"
    cleaned_df.to_csv(cleaned_path, index=False)

    print(f"Profile report saved to {profile_path}")
    print(f"Cleaned data saved to {cleaned_path}")
    print(f"Cleaned row count: {len(cleaned_df)}")


if __name__ == "__main__":
    main()