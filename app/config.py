from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    rabbitmq_url: str
    task_queue_name: str
    cors_allow_origins: str
    cors_allow_credentials: bool
    cors_allow_methods: str
    cors_allow_headers: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @staticmethod
    def _parse_csv(value: str) -> list[str]:
        if value == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    @property
    def parsed_cors_allow_origins(self) -> list[str]:
        return self._parse_csv(self.cors_allow_origins)

    @property
    def parsed_cors_allow_methods(self) -> list[str]:
        return self._parse_csv(self.cors_allow_methods)

    @property
    def parsed_cors_allow_headers(self) -> list[str]:
        return self._parse_csv(self.cors_allow_headers)


settings = Settings()
