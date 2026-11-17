import os
import boto3
from botocore.client import Config
from pathlib import Path
from typing import Optional, BinaryIO
from backend.core.config import settings

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_S3_FALLBACK_DIR = ROOT_DIR / "data" / "s3_storage"

class StorageManager:
    def __init__(self):
        self.s3_endpoint = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.secure = settings.S3_SECURE
        self._s3_client = None
        self._is_live = False

        try:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=self.s3_endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version="s3v4", connect_timeout=1, read_timeout=1, retries={"max_attempts": 0}),
                use_ssl=self.secure,
            )
            # Ping bucket list
            self._s3_client.list_buckets()
            self._is_live = True
        except Exception:
            self._is_live = False
            # Ensure local fallback directory structure
            for bucket in [settings.S3_BUCKET_RAW, settings.S3_BUCKET_INTERMEDIATES, settings.S3_BUCKET_RESULTS, settings.S3_BUCKET_REFERENCE]:
                (LOCAL_S3_FALLBACK_DIR / bucket).mkdir(parents=True, exist_ok=True)

    def is_connected(self) -> bool:
        return self._is_live

    def generate_presigned_upload_url(self, bucket: str, key: str, expires_in: int = 3600) -> dict:
        """
        Generates presigned upload URL directly to S3.
        In local fallback mode, points to the local backend upload route.
        """
        if self._is_live and self._s3_client:
            url = self._s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return {"upload_url": url, "method": "PUT", "s3_uri": f"s3://{bucket}/{key}", "storage_tier": "minio"}
        else:
            # Fallback local direct route
            fallback_url = f"/api/v1/datasets/upload-direct?bucket={bucket}&key={key}"
            return {"upload_url": fallback_url, "method": "POST", "s3_uri": f"s3://{bucket}/{key}", "storage_tier": "local_fallback"}

    def put_bytes(self, bucket: str, key: str, data: bytes) -> str:
        s3_uri = f"s3://{bucket}/{key}"
        if self._is_live and self._s3_client:
            self._s3_client.put_object(Bucket=bucket, Key=key, Body=data)
        else:
            dest = LOCAL_S3_FALLBACK_DIR / bucket / key
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        return s3_uri

    def get_stream(self, bucket: str, key: str) -> BinaryIO:
        """
        Returns a streaming file-like binary reader for O(1) RAM reading.
        """
        if self._is_live and self._s3_client:
            response = self._s3_client.get_object(Bucket=bucket, Key=key)
            return response["Body"]
        else:
            local_path = LOCAL_S3_FALLBACK_DIR / bucket / key
            if not local_path.exists():
                raise FileNotFoundError(f"Storage object not found: {bucket}/{key}")
            return open(local_path, "rb")

    def put_file(self, bucket: str, key: str, file_path: str) -> str:
        s3_uri = f"s3://{bucket}/{key}"
        if self._is_live and self._s3_client:
            self._s3_client.upload_file(file_path, bucket, key)
        else:
            dest = LOCAL_S3_FALLBACK_DIR / bucket / key
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "rb") as src, open(dest, "wb") as dst:
                while chunk := src.read(65536):
                    dst.write(chunk)
        return s3_uri

storage_manager = StorageManager()
