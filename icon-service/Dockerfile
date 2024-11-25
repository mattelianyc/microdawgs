FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV MODEL_PATH="/app/models"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE="/app/models/cache"
ENV PIP_DEFAULT_TIMEOUT=1000

# Install system dependencies and clean up in one layer
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create model cache directory
RUN mkdir -p /app/models/cache \
    && chmod -R 777 /app/models

# Copy requirements and installation script
COPY requirements.txt install_packages.sh ./
RUN chmod +x install_packages.sh

# Run installation script with retries
RUN ./install_packages.sh || exit 1

# Clean up
RUN rm -rf ~/.cache/pip \
    && pip3 cache purge \
    && rm install_packages.sh

# Copy application code
COPY . .

# Add volume for model cache
VOLUME ["/app/models"]

# Run the application with hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
