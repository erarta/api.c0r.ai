# Multi-stage build for optimized production image
FROM python:3.11-alpine as builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    curl

# Create virtual environment
RUN python -m venv /opt/venv

# Copy requirements first for better caching
COPY services/api/public/api-requirements.txt ./api-requirements.txt

# Install Python dependencies
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip
RUN /opt/venv/bin/pip install --no-cache-dir -r api-requirements.txt

# Production stage
FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    curl

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Alpine: use addgroup/adduser
RUN addgroup -S apiuser && adduser -S apiuser -G apiuser && \
    chown -R apiuser:apiuser /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY services/api/public/ .
COPY common/ ./common/
COPY shared/ ./shared/

# Set proper permissions
RUN chown -R apiuser:apiuser /app

# Switch to non-root user
USER apiuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# Expose port
EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

# Run the API application (expects services/api/public/main.py)
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020", "--workers", "1", "--loop", "asyncio", "--access-log", "--log-level", "info"]
