FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY services/ml/requirements.txt ./ml-requirements.txt

# Install Python dependencies
ENV PIP_DEFAULT_TIMEOUT=180
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r ml-requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "services.ml.main:app", "--host", "0.0.0.0", "--port", "8001"]