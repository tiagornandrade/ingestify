import os
import json
import logging
import pandas as pd
from io import BytesIO
from kafka import KafkaConsumer
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
KAFKA_TOPICS = os.getenv('KAFKA_TOPICS', 'user-events,order-events').split(',')
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'MB30ZIE4qBwPSS775NBB')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'FqHf5e2fuWilZPPVeYQWkgIdhjmANQ9tAyDEjTL6')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'data-lake')

consumer = KafkaConsumer(
    *KAFKA_TOPICS,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


def save_to_minio(df, bucket_name, object_name):
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )

        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        minio_client.put_object(
            bucket_name,
            object_name,
            data=buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )

        logger.info(f'File {object_name} successfully saved to bucket {bucket_name}.')

    except Exception as e:
        logger.error(f"Error saving the file to MinIO: {e}")


def consume_and_save():
    messages = []

    for message in consumer:
        topic = message.topic
        messages.append(message.value)

        if len(messages) >= 100:
            file_name = f"{topic.replace('-', '_')}/{topic.replace('-', '_')}_file.parquet"

            if messages:
                df = pd.DataFrame(messages)
                save_to_minio(df, BUCKET_NAME, file_name)

            messages = []


if __name__ == "__main__":
    consume_and_save()
