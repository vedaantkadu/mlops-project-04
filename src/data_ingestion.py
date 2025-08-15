import os
import pandas as pd
from google.cloud import storage
import gcsfs
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_names = self.config["bucket_file_names"]
        self.large_file = self.config.get("large_file", "animelist.csv")

        os.makedirs(RAW_DIR, exist_ok=True)
        logger.info("Data Ingestion Initialized")

    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR, file_name)

                if file_name == self.large_file:
                    logger.info(f"Large file '{file_name}' detected — streaming only 5M rows.")
                    fs = gcsfs.GCSFileSystem(project=client.project)
                    gcs_path = f"{self.bucket_name}/{file_name}"

                    with fs.open(gcs_path, 'rb') as f:
                        df = pd.read_csv(f, nrows=5_000_000)
                        df.to_csv(file_path, index=False)

                    logger.info(f"Saved first 5M rows of '{file_name}' to {file_path}")

                else:

                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)
                    logger.info(f"Downloaded smaller file: {file_name}")

        except Exception as e:
            logger.error(f"Error while downloading data from GCP: {e}")
            raise CustomException(f"Failed to download data: {e}")

    def run(self):
        try:
            logger.info("Starting Data Ingestion Process...")
            self.download_csv_from_gcp()
            logger.info("Data Ingestion Completed Successfully")
        except CustomException as ce:
            logger.error(f"CustomException: {str(ce)}")
        finally:
            logger.info("Data Ingestion DONE")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()
