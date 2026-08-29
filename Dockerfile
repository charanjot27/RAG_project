FROM python:3.11-slim

WORKDIR /app

# Keep Python lean and predictable inside the container.
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.hf_cache

# Install deps first so this layer caches across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake the ML models into the image so the first request is fast (no cold-start
# download). Comment this out if you prefer a smaller image + lazy download.
RUN python -m scripts.preload_models

EXPOSE 8000
# Render/Railway/Fly inject $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
