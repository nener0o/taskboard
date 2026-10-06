import logging
from pathlib import Path

from botocore.exceptions import ClientError

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.seed import seed

logger = logging.getLogger("taskboard.migrate")


def ensure_bucket() -> None:
    if not settings.s3_enabled:
        return
    import time

    import boto3

    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )
    last_error: Exception | None = None
    for _attempt in range(8):
        try:
            try:
                client.head_bucket(Bucket=settings.s3_bucket)
            except ClientError:
                client.create_bucket(Bucket=settings.s3_bucket)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(1)
    raise RuntimeError("Объектное хранилище не ответило") from last_error


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    ensure_bucket()
    if settings.seed_demo:
        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        init_db()
    except Exception:
        logger.exception("Миграция не выполнена")
        raise SystemExit(1)
    logger.info("Схема базы актуальна")
