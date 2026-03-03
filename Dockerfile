FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ /app/requirements/

# Install development dependencies for testing
RUN pip install --upgrade pip && \
    pip install -r requirements/development.txt

COPY . /app/

RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chmod +x /app/scripts/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
