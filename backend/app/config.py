from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "TaskBoard"
    database_url: str = "sqlite:///./taskboard.db"
    jwt_secret: str = "dev-only-change-me-please-32bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    seed_demo: bool = True
    storage_dir: str = "./storage"
    s3_endpoint: str | None = None
    s3_bucket: str = "taskboard"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "us-east-1"
    public_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:5173"
    weather_lat: float = 55.7558
    weather_lon: float = 37.6173
    weather_location: str = "Москва"
    max_upload_bytes: int = 5 * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def s3_enabled(self) -> bool:
        return bool(self.s3_endpoint and self.s3_access_key and self.s3_secret_key)


settings = Settings()
