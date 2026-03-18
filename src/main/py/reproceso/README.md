# Reproceso del motor de calidad (Databricks Apps / Flask)

App Flask para subir archivos `.csv` y registrar por fila:

- `nbrtabla`
- `codapp`
- `fecrutina`

La app inserta esas filas en una tabla (local o Databricks).

## Logo

Guarda el logo como:

- `src/main/py/reproceso/static/logo.png`

## Local (Docker + Postgres)

- `docker compose -f devops/docker-compose.yml up --build`
- Abrir: http://localhost:8080

Variables:
- `DATABASE_URL` (default dentro de compose)
- `TARGET_TABLE` (default `reproceso_registros`)

## Databricks SQL

La app intentará usar Databricks por defecto cuando existan estas variables del entorno de Databricks Apps. Si no están, usará Postgres local.

Variables base esperadas:

- `DATABRICKS_APP_NAME`
- `DATABRICKS_APP_PORT`
- `DATABRICKS_CLIENT_ID`
- `DATABRICKS_CLIENT_SECRET`
- `DATABRICKS_HOST`

Tabla objetivo (tu caso):
- `catalog_lhcl_desa_bcp.bcp_ddv_gobierno_motorescalidad.m_reproceso`

Notas:
- Si la tabla no existe, la app la crea como **Delta** (`USING DELTA`).
- En Databricks Apps, el puerto se toma automáticamente desde `PORT` o `DATABRICKS_APP_PORT`.
