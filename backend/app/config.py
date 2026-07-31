"""Настройки приложения — грузим все из .env через Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Главный конфиг приложения, все значения берутся из переменных окружения."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Приложение
    app_name: str = "AI Support Agent"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # База данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_support_agent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Безопасность
    secret_key: str = "CHANGE_ME_USE_AT_LEAST_32_CHARACTERS_RANDOM_STRING"  # noqa: S105
    access_token_expire_minutes: int = 30
    cors_origins: str = "http://localhost,http://localhost:3000,http://localhost:5173"

    # AI провайдеры
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Администратор по умолчанию (первый запуск)
    admin_email: str = "admin@company.com"
    admin_name: str = "Admin"
    admin_default_password: str = "Admin123"  # noqa: S105

    # Файлы
    upload_dir: str = "uploads"
    max_file_size: int = 52_428_800  # 50MB

    @property
    def cors_origins_list(self) -> list[str]:
        """Парсим CORS_ORIGINS строку в список."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
