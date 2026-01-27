# Ubuntu Server Monitoring & Reporting System - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Korean fonts
RUN apt-get update && apt-get install -y \
    procps \
    curl \
    fonts-nanum \
    fonts-nanum-coding \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p logs data/metrics reports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

# Default command (can be overridden)
CMD ["python", "src/main.py", "--collect-only"]
