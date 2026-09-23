import json
import csv
from google.cloud import storage, bigquery
import logging
logger = logging.getLogger(__name__)

# JSON Output
def save_json(data, filename):
    with open(filename, 'w',encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    logger.info('Data successfully saved to %s', filename)

# CSV Output
def save_csv(data, filename):
    if not data:
        logger.warning('No data to save.')
        return
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    logger.info('Data successfully saved %d records to %s', len(data), filename)

def upload_to_gcs(local_file, bucket_name, destination_blob):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(local_file)

    logger.info(
        "Uploaded %s to gs://%s/%s",
        local_file,
        bucket_name,
        destination_blob
    ) 


def load_gcs_csv_to_bigquery(bucket_id, blob_name, project_id, dataset_id, table_id, location):
    client = bigquery.Client(project = project_id)
    source_uri = f"gs://{bucket_id}/{blob_name}"
    destination_table =(f"{project_id}.{dataset_id}.{table_id}")

    job_config = bigquery.LoadJobConfig(
        schema=[
             bigquery.SchemaField("id", "INTEGER"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("street", "STRING"),
            bigquery.SchemaField("month", "STRING")
        ], source_format = bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=(
            bigquery.WriteDisposition.WRITE_TRUNCATE
        )
    )

    load_job = client.load_table_from_uri(
        source_uri,
        destination_table,
        job_config = job_config,
        location = location
    )

    load_job.result()

    table = client.get_table(
        destination_table
    )

    logger.info("Loaded %d rows into BigQuery table %s", table.num_rows, destination_table)