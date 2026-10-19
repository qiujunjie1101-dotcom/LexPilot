"""MinIO / S3 文件上传与对象存储适配器。

当前合同正文以文本列存储；接入对象存储后由本适配器接管原始文件，
调用方只需依赖 upload / download 两个方法。
"""
from __future__ import annotations

import os
from typing import Any


class MinioStorage:
    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        secure: bool | None = None,
    ) -> None:
        self.endpoint = endpoint or os.getenv('MINIO_ENDPOINT', '')
        self.access_key = access_key or os.getenv('MINIO_ACCESS_KEY', '')
        self.secret_key = secret_key or os.getenv('MINIO_SECRET_KEY', '')
        self.bucket = bucket or os.getenv('MINIO_BUCKET', 'contracts')
        self.secure = secure if secure is not None else os.getenv('MINIO_SECURE', 'false').lower() in {'1', 'true', 'yes', 'on'}

    def _client(self) -> Any:
        try:
            from minio import Minio
        except ImportError as exc:
            raise RuntimeError('MINIO_ENABLED requires the optional "minio" package') from exc
        return Minio(self.endpoint, access_key=self.access_key, secret_key=self.secret_key, secure=self.secure)

    def upload(self, object_name: str, data: bytes, content_type: str = 'application/octet-stream') -> str:
        from io import BytesIO

        client = self._client()
        if not client.bucket_exists(self.bucket):
            client.make_bucket(self.bucket)
        client.put_object(self.bucket, object_name, BytesIO(data), length=len(data), content_type=content_type)
        return object_name

    def download(self, object_name: str) -> bytes:
        client = self._client()
        response = client.get_object(self.bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
