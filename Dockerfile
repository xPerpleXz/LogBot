# Discord Log Bot Dockerfile
FROM python:3.11-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# Verhindere Python Buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# System Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# App Code kopieren
COPY bot.py .
COPY admin_tools.py .
COPY setup.py .

# Optionale Dateien (werden ignoriert wenn nicht vorhanden)
COPY .env* ./
COPY credentials.json* ./

# User für Sicherheit
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Start Command
CMD ["python", "-u", "bot.py"]
