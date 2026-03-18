import os
from typing import Sequence

from sqlalchemy import MetaData, String, Table, Column, Date, create_engine

from .storage import ReprocesoRow, Storage


class PostgresStorage(Storage):
    def __init__(self, database_url: str, table_name: str):
        self._database_url = database_url
        self._table_name = table_name
        self._engine = create_engine(self._database_url, pool_pre_ping=True)
        self._table: Table | None = None

    @classmethod
    def from_env(cls) -> "PostgresStorage":
        database_url = os.getenv("DATABASE_URL") or "postgresql+psycopg2://app:app@db:5432/app"
        table_name = os.getenv("TARGET_TABLE") or "reproceso_registros"
        return cls(database_url=database_url, table_name=table_name)

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def backend_name(self) -> str:
        return "Postgres local"

    def ensure_schema(self) -> None:
        metadata = MetaData()
        self._table = Table(
            self._table_name,
            metadata,
            Column("nbrtabla", String(256), nullable=False),
            Column("codapp", String(128), nullable=False),
            Column("fecrutina", Date(), nullable=False),
        )
        metadata.create_all(self._engine)

    def insert_rows(self, rows: Sequence[ReprocesoRow]) -> int:
        if not rows:
            return 0
        if self._table is None:
            self.ensure_schema()
        assert self._table is not None

        payload = [
            {"nbrtabla": r.nbrtabla, "codapp": r.codapp, "fecrutina": r.fecrutina}
            for r in rows
        ]
        with self._engine.begin() as conn:
            conn.execute(self._table.insert(), payload)
        return len(rows)
