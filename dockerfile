FROM python:3.11-slim

WORKDIR /app/twilios_version
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

COPY . .

# Puerto interno (pon un proxy TLS delante)
EXPOSE 8080
CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "-w", "1", "-b", "0.0.0.0:8080", "app:app"]
