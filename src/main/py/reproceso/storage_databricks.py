import os
from typing import Sequence

from .storage import ReprocesoRow, Storage


class DatabricksStorage(Storage):
    def __init__(
        self,
        server_hostname: str,
        http_path: str,
        access_token: str | None,
        table_name: str,
        host: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        app_name: str | None = None,
    ):
        self._server_hostname = server_hostname
        self._http_path = http_path
        self._access_token = access_token
        self._table_name = table_name
        self._host = host
        self._client_id = client_id
        self._client_secret = client_secret
        self._app_name = app_name or "reproceso-calidad"

    @staticmethod
    def _normalize_host(host: str | None) -> str | None:
        if not host:
            return None
        normalized = host.strip().rstrip("/")
        if normalized.startswith("https://"):
            normalized = normalized[len("https://"):]
        elif normalized.startswith("http://"):
            normalized = normalized[len("http://"):]
        return normalized or None

    @classmethod
    def from_env(cls) -> "DatabricksStorage":
        raw_host = os.getenv("DATABRICKS_SERVER_HOSTNAME") or os.getenv("DATABRICKS_HOST")
        server_hostname = cls._normalize_host(raw_host)
        if not server_hostname:
            raise RuntimeError(
                "Falta DATABRICKS_SERVER_HOSTNAME o DATABRICKS_HOST para conectar a Databricks SQL"
            )

        http_path = os.getenv("DATABRICKS_HTTP_PATH") or os.getenv("DATABRICKS_SQL_HTTP_PATH")
        if not http_path:
            raise RuntimeError(
                "Falta DATABRICKS_HTTP_PATH. Debes usar el HTTP Path del SQL Warehouse o compute SQL endpoint."
            )

        access_token = os.getenv("DATABRICKS_TOKEN")
        host = os.getenv("DATABRICKS_HOST")
        client_id = os.getenv("DATABRICKS_CLIENT_ID")
        client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
        app_name = os.getenv("DATABRICKS_APP_NAME")
        table_name = (
            os.getenv("TARGET_TABLE")
            or "catalog_lhcl_desa_bcp.bcp_ddv_gobierno_motorescalidad.m_reproceso"
        )
        return cls(
            server_hostname=server_hostname,
            http_path=http_path,
            access_token=access_token,
            table_name=table_name,
            host=host,
            client_id=client_id,
            client_secret=client_secret,
            app_name=app_name,
        )

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def backend_name(self) -> str:
        return "Databricks SQL"

    def _connect(self):
        from databricks import sql

        kwargs = {
            "server_hostname": self._server_hostname,
            "http_path": self._http_path,
            "user_agent_entry": self._app_name,
        }
        if self._access_token:
            kwargs["access_token"] = self._access_token
        elif self._client_id and self._client_secret:
            from databricks.sdk.core import Config, oauth_service_principal

            host = self._host or f"https://{self._server_hostname}"

            def credential_provider():
                config = Config(
                    host=host,
                    client_id=self._client_id,
                    client_secret=self._client_secret,
                )
                return oauth_service_principal(config)

            kwargs["credentials_provider"] = credential_provider
        else:
            raise RuntimeError(
                "Falta autenticacion para Databricks SQL. Usa DATABRICKS_TOKEN o DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET."
            )
        return sql.connect(**kwargs)

    def ensure_schema(self) -> None:
        # Minimal schema as requested: 3 fields, explicitly as Delta table (UC).
        ddl = (
            f"CREATE TABLE IF NOT EXISTS {self._table_name} ("
            "nbrtabla STRING, codapp STRING, fecrutina DATE) "
            "USING DELTA"
        )
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(ddl)

    def insert_rows(self, rows: Sequence[ReprocesoRow]) -> int:
        if not rows:
            return 0
        self.ensure_schema()

        sql_stmt = f"INSERT INTO {self._table_name} (nbrtabla, codapp, fecrutina) VALUES (?, ?, ?)"
        params = [(r.nbrtabla, r.codapp, r.fecrutina) for r in rows]
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql_stmt, params)
        return len(rows)
