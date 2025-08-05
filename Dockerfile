FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        libpq-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for data and models
RUN mkdir -p /app/data/generated/images \
    && mkdir -p /app/data/generated/videos \
    && mkdir -p /app/data/generated/audio \
    && mkdir -p /app/models \
    && mkdir -p /app/monitoring/logs

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
