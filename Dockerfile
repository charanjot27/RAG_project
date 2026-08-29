FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal; add build tools only if a wheel needs compiling.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
