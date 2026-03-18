import os
from dataclasses import dataclass
from datetime import date
from typing import Sequence


@dataclass(frozen=True)
class ReprocesoRow:
    nbrtabla: str
    codapp: str
    fecrutina: date | None


class Storage:
    @property
    def table_name(self) -> str:
        raise NotImplementedError

    @property
    def backend_name(self) -> str:
        raise NotImplementedError

    def ensure_schema(self) -> None:
        raise NotImplementedError

    def insert_rows(self, rows: Sequence[ReprocesoRow]) -> int:
        raise NotImplementedError


def get_storage() -> Storage:
    has_databricks_env = all(
        [
            os.getenv("DATABRICKS_HOST"),
            os.getenv("DATABRICKS_CLIENT_ID"),
            os.getenv("DATABRICKS_CLIENT_SECRET"),
        ]
    )

    if has_databricks_env:
        from .storage_databricks import DatabricksStorage

        return DatabricksStorage.from_env()

    from .storage_postgres import PostgresStorage

    return PostgresStorage.from_env()
