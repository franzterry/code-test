import io
from datetime import date, datetime

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for

from .storage import ReprocesoRow, get_storage


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _parse_rows(df: pd.DataFrame) -> list[ReprocesoRow]:
    df = _normalize_columns(df)
    required = {"nbrtabla", "codapp", "fecrutina"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"CSV debe contener columnas: {', '.join(sorted(required))}. Faltan: {', '.join(missing)}")

    out: list[ReprocesoRow] = []

    for i in range(len(df)):
        nbrtabla = str(df.at[i, "nbrtabla"]).strip()
        codapp = str(df.at[i, "codapp"]).strip()
        fecrutina_raw = str(df.at[i, "fecrutina"]).strip()

        if not nbrtabla or nbrtabla.lower() == "nan":
            raise ValueError(f"Fila {i+1}: nbrtabla es obligatorio")
        if not codapp or codapp.lower() == "nan":
            raise ValueError(f"Fila {i+1}: codapp es obligatorio")

        if not fecrutina_raw or fecrutina_raw.lower() == "nan":
            raise ValueError(f"Fila {i+1}: fecrutina es obligatoria y debe venir como YYYY-MM-DD")

        try:
            fecrutina: date = datetime.strptime(fecrutina_raw, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Fila {i+1}: fecrutina '{fecrutina_raw}' inválida (formato esperado YYYY-MM-DD)"
            )

        out.append(ReprocesoRow(nbrtabla=nbrtabla, codapp=codapp, fecrutina=fecrutina))

    return out


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "reproceso-dev"  # solo local; en Databricks configura SECRET_KEY

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/upload")
    def upload():
        f = request.files.get("file")
        if not f or not f.filename:
            flash("Selecciona un archivo .csv", "error")
            return redirect(url_for("index"))

        if not f.filename.lower().endswith(".csv"):
            flash("El archivo debe ser .csv", "error")
            return redirect(url_for("index"))

        try:
            content = f.read()
            df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
            rows = _parse_rows(df)

            storage = get_storage()
            storage.ensure_schema()
            inserted = storage.insert_rows(rows)

            preview = _normalize_columns(df).head(20).to_dict(orient="records")
            flash(f"OK: {inserted} filas ingresadas", "success")
            upload_result = {
                "filename": f.filename,
                "inserted": inserted,
                "table_name": storage.table_name,
                "backend_name": storage.backend_name,
            }
            return render_template("index.html", preview=preview, upload_result=upload_result)
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("index"))

    return app


app = create_app()
