# s3_client.py
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import os
import logging

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
BUCKET_NAME = os.getenv('MINIO_BUCKET', 'bionicpro-reports')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
PUBLIC_MINIO_URL = os.getenv('PUBLIC_MINIO_URL', 'http://localhost:8083')

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name='us-east-1',
    config=boto3.session.Config(signature_version='s3v4'),
    use_ssl=MINIO_SECURE
)


def get_report_key(email: str) -> str:
    return f"reports/{email.lower().strip()}/latest.pdf"


def upload_report_to_s3(pdf_bytes: bytes, email: str):
    key = get_report_key(email)
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=pdf_bytes,
            ContentType='application/pdf',
            Metadata={
                'email': email,
                'generated_at': datetime.utcnow().isoformat()
            }
        )
        logger.info(f"Отчёт успешно загружен в MinIO: {key}")
    except ClientError as e:
        logger.error(f"Ошибка загрузки в MinIO: {e}")
        raise


def get_presigned_url(email: str, expires_in: int = 3600) -> str | None:
    """
    Возвращает presigned URL ТОЛЬКО если файл действительно существует в бакете.
    Если файла нет — возвращает None (чтобы запустилась генерация).
    """
    key = get_report_key(email)

    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=key)
        logger.info(f"Файл найден в MinIO: {key}")

        public_client = boto3.client(
            's3',
            endpoint_url=PUBLIC_MINIO_URL,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name='us-east-1',
            config=boto3.session.Config(signature_version='s3v4'),
            use_ssl=MINIO_SECURE
        )

        url = public_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=expires_in
        )
        return url

    except ClientError as e:
        if e.response['Error']['Code'] == '404' or e.response['Error']['Code'] == 'NoSuchKey':
            logger.info(f"Файл отсутствует в MinIO: {key} → будет сгенерирован")
            return None
        else:
            logger.error(f"Ошибка при проверке файла в MinIO: {e}")
            return None