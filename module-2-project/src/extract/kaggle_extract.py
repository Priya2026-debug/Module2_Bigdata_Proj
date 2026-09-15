# you could use kagglehub to download the dataset and then the Google Cloud Storage Python library to upload it.
import os

import kagglehub
from google.cloud import storage


def extract_kaggle_to_gcs():

    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]

    print("GCP Project:", GCP_PROJECT_ID)
    print("GCS Bucket:", GCS_BUCKET_NAME)

    # 1. Download dataset from Kaggle
    path = kagglehub.dataset_download(
        "olistbr/brazilian-ecommerce"
    )

    print("Downloaded to:", path)

    # 2. Connect to GCS
    client = storage.Client(project=GCP_PROJECT_ID)

    bucket = client.bucket(GCS_BUCKET_NAME)

    print("Connected to bucket:", bucket.name)

    # 3. Upload files
    for filename in os.listdir(path):

        local_file = os.path.join(path, filename)

        if os.path.isfile(local_file):

            blob = bucket.blob(
                f"raw/kaggle/{filename}"
            )

            blob.upload_from_filename(local_file)

            print(f"Uploaded: {filename}")
