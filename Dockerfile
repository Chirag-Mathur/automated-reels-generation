# Base image with Python 3.9 and Debian (ffmpeg-friendly)
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set environment variable for Python to not buffer logs
ENV PYTHONUNBUFFERED=1

# Load environment variables from .env manually (Railway will also inject them)
ENV ENV_FILE=.env

# Entry command (your scheduler)
CMD ["python", "-m", "app.scheduler.cron"]
