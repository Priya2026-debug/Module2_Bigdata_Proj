# Create big querry data set 
import os

from google.cloud import bigquery


def load_gcs_to_bigquery():

    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
    GCS_DATASET_ID = os.environ["GCS_DATASET_ID"]

    print("GCP Project:", GCP_PROJECT_ID)
    print("GCS Bucket:", GCS_BUCKET_NAME)
    print("BigQuery Dataset:", GCS_DATASET_ID)

    client = bigquery.Client(project=GCP_PROJECT_ID)

    print("Connected to BigQuery!")

    # Create BigQuery dataset
    dataset_ref = f"{GCP_PROJECT_ID}.{GCS_DATASET_ID}"

    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "asia-southeast1"

    client.create_dataset(dataset, exists_ok=True)

    print(f"BigQuery dataset ready: {dataset_ref}")

    files = [
        "olist_sellers_dataset.csv",
        "product_category_name_translation.csv",
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_customers_dataset.csv",
        "olist_geolocation_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "olist_products_dataset.csv"
    ]

    for filename in files:

        table_name = filename.replace(".csv", "")
        table_name = table_name.replace("_dataset", "")

        table_id = (
            f"{GCP_PROJECT_ID}."
            f"{GCS_DATASET_ID}."
            f"{table_name}"
        )

        uri = (
            f"gs://{GCS_BUCKET_NAME}/"
            f"raw/kaggle/{filename}"
        )

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            allow_quoted_newlines=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )

        print(f"Loading {filename} → {table_id}")

        load_job = client.load_table_from_uri(
            uri,
            table_id,
            job_config=job_config
        )

        load_job.result()

        print(f"✓ Loaded: {table_name}")
