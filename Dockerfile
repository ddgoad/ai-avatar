# Multi-stage Dockerfile for AI Avatar Container Apps deployment
# Python 3.11 base image as specified in TDD

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (ffmpeg for audio processing, GStreamer for Azure Speech SDK)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/static/audio /app/static/backgrounds /tmp/avatars \
    && chown -R appuser:appuser /app /tmp/avatars

# Switch to non-root user
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port 5000 (Flask default)
EXPOSE 5000

# Production stage
FROM base as runtime

# Set Flask environment
ENV FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

# Use Gunicorn WSGI server for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "src.app:create_app()"]