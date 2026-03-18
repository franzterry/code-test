FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY src/main/py/reproceso/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/main/py/reproceso /app/src/main/py/reproceso
COPY devops/entrypoint.sh /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src/main/py
ENV FLASK_APP=reproceso.app
EXPOSE 8080

RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
