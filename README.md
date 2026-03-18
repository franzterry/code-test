# code-test

Estructura creada para una app tipo **Databricks Apps** usando **Flask**.

- App: `src/main/py/reproceso/app.py`
- Docker local: `devops/docker-compose.yml` (Flask + Postgres)

## Ejecutar en local

- `docker compose -f devops/docker-compose.yml up --build`
- Abrir: http://localhost:8080

Más detalles en `src/main/py/reproceso/README.md`.

