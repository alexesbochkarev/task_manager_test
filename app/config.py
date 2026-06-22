from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/task_manager"
    cors_allow_origins: str = "*"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @staticmethod
    def _parse_csv(value: str) -> list[str]:
        if value == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

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
