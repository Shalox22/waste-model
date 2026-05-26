FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and headless OpenGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies with a longer timeout for slow networks
RUN pip install --no-cache-dir -r requirements.txt \
    --default-timeout=100 \
    --retries=10

# One copy keeps layers simple; changing only code invalidates from here down (not pip).
COPY src/ ./src/
COPY model/ ./model/

WORKDIR /app/src

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import os, requests; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"8080\")}/')" || exit 1

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
