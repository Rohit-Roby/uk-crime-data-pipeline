import os
import logging
from dotenv import load_dotenv
from extract import fetch_crime_data
from transform import clean_records
from load import save_json, save_csv, upload_to_gcs, load_gcs_csv_to_bigquery
from pathlib import Path
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # Create logs directory if it doesn't exist


# LOGGING CONFIGURATION
logging.basicConfig(
    level = logging.INFO,
    format = ("%(asctime)s | "
             "%(levelname)s | "
             "%(name)s | " 
             "%(message)s"),
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR / "crime_pipeline.log", encoding="utf-8"
        )
    ]
)
logger = logging.getLogger(__name__)


# LOADING ENVIRONMENT VARIABLES
load_dotenv()  # Load environment variables from .env file

def main():

    logger.info("pipeline started")

    url = os.getenv('POLICE_API_URL')
    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION")
    dataset_id = os.getenv("BIGQUERY_DATASET")
    table_id = os.getenv("BIGQUERY_TABLE")


    params = {
        'date': os.getenv('CRIME_DATE'),
        'lat': float(os.getenv('LATITUDE')),
        'lng': float(os.getenv('LONGITUDE'))
        }
    logger.info("Fetching crime data for date: %s", params['date'])

    raw_data = fetch_crime_data(url, params)
    logger.info('Fetched %d records from APi', len(raw_data))

    cleaned_data = clean_records(raw_data)

    if not cleaned_data:
        logger.warning('No cleaned data available . Pipeline stopped.')
        return
        

    jsonfilename = 'data/cleaned_crime_data.json'
    csvfilename = 'data/cleaned_crime_data.csv'


    save_json(cleaned_data, jsonfilename)
    save_csv(cleaned_data, csvfilename)

    # LOADING CLEANED DATA TO GCP BUCKET
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    crime_date = os.getenv('CRIME_DATE')
    json_blob = f"cleaned/{crime_date}/cleaned_crime_data.json"
    csv_blob = f"cleaned/{crime_date}/cleaned_crime_data.csv"

    upload_to_gcs(jsonfilename, bucket_name, json_blob)
    upload_to_gcs(csvfilename, bucket_name, csv_blob)


    load_gcs_csv_to_bigquery(
        bucket_id=bucket_name,
        blob_name=csv_blob,
        project_id=project_id,
        dataset_id=dataset_id,
        table_id=table_id,
        location=region
        )

    logger.info('Pipeline completed successfully. Cleaned data saved at %s and %s ', jsonfilename, csvfilename)
if __name__ == "__main__":
    main()