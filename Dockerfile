FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    ANY2SCREEN_UPLOAD_ROOT=/data/uploads

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libfontconfig1 \
    libfreetype6 \
    libgdk-pixbuf-2.0-0 \
    libharfbuzz0b \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY scripts ./scripts
COPY src ./src

RUN pip install --no-cache-dir -e '.[web]'
RUN python -m playwright install chromium
EXPOSE 8000

CMD ["python", "src/cli.py", "web", "--host", "0.0.0.0", "--port", "8000"]
