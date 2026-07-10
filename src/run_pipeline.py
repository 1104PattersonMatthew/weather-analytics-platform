import subprocess
import sys
from pathlib import Path


def get_project_root():
    return Path(__file__).resolve().parents[1]


def run_step(step_name, script_name):
    project_root = get_project_root()
    script_path = project_root / "src" / script_name

    print("=" * 60)
    print(f"Running step: {step_name}")
    print("=" * 60)

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=project_root,
        check=True
    )

    print(f"Completed step: {step_name}")


def main():
    steps = [
        ("Extract raw weather data from Open-Meteo", "extract.py"),
        ("Profile and clean weather data with pandas", "profile_clean.py"),
        ("Load cleaned data into PostgreSQL", "load.py"),
    ]

    try:
        for step_name, script_name in steps:
            run_step(step_name, script_name)

        print("=" * 60)
        print("Weather analytics pipeline completed successfully.")
        print("=" * 60)

    except subprocess.CalledProcessError as error:
        print(f"Pipeline failed while running: {error.cmd}")
        print(f"Exit code: {error.returncode}")
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()