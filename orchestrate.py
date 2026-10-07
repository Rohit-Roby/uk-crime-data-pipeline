import os
import logging
import subprocess
from datetime import datetime

from dotenv import load_dotenv
from main import main as run_ingestion


logger = logging.getLogger(__name__)
load_dotenv()


import requests


def get_crime_date(configured_date=None):

    if configured_date:
        try:
            datetime.strptime(
                configured_date,
                "%Y-%m"
            )
        except ValueError:
            raise ValueError(
                "CRIME_DATE should use YYYY-MM format"
            )

        return configured_date

    response = requests.get(
        "https://data.police.uk/api/crime-last-updated",
        timeout=10
    )

    response.raise_for_status()

    latest_date = response.json()["date"]

    parsed_date = datetime.strptime(
        latest_date,
        "%Y-%m-%d"
    )

    return parsed_date.strftime("%Y-%m")


def convert_crime_date(crime_date):
    parsed_date = datetime.strptime(
        crime_date,
        "%Y-%m"
    )

    return parsed_date.strftime("%Y-%m-01")


def run_dbt(crime_month):
    dbt_vars = (
        f'{{crime_month: "{crime_month}"}}'
    )

    subprocess.run(
        [
            "dbt",
            "build",
            "--project-dir",
            "crime_dbt",
            "--profiles-dir",
            "crime_dbt",
            "--no-partial-parse",
            "--vars",
            dbt_vars
        ],
        check=True
    )


def orchestrate():
    configured_date = os.getenv("CRIME_DATE")

    crime_date = get_crime_date(
        configured_date
    )

    os.environ["CRIME_DATE"] = crime_date

    crime_month = convert_crime_date(
        crime_date
    )

    logger.info(
        "Starting pipeline for %s",
        crime_date
    )

    ingestion_success = run_ingestion()

    if not ingestion_success:
        raise RuntimeError(
            "Ingestion failed or returned no data"
        )

    logger.info(
        "Ingestion completed. Starting dbt for %s",
        crime_month
    )

    run_dbt(crime_month)

    logger.info(
        "Full pipeline completed successfully"
    )


if __name__ == "__main__":
    orchestrate()