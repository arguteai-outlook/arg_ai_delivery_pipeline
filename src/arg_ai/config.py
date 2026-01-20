import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def dsn(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.name} user={self.user} password={self.password}"


def get_db_config() -> DbConfig:
    return DbConfig(
        host=os.getenv("ARG_AI_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("ARG_AI_DB_PORT", "5432")),
        name=os.getenv("ARG_AI_DB_NAME", "arg_ai"),
        user=os.getenv("ARG_AI_DB_USER", "arg_ai"),
        password=os.getenv("ARG_AI_DB_PASSWORD", "arg_ai"),
    )
