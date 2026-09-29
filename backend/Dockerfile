# ==============================================================================
# NWIS (Nearby Wells Intelligence System) - Backend & AI Dockerfile
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential, postgres client lib, tesseract-ocr)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN pip install --no-cache-dir pymupdf pytesseract sentence-transformers faiss-cpu

# Copy backend, AI module, and pre-computed data artifacts
COPY backend /app/backend
COPY ai /app/ai
COPY data /app/data

# Ensure root and backend are both on PYTHONPATH
ENV PYTHONPATH="/app:/app/backend"
WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
