FROM python:3.9

WORKDIR /app

# Create persistent directories
RUN mkdir -p /app/shared/models /app/shared/cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install script
COPY requirements.txt install_packages.sh ./
RUN chmod +x install_packages.sh

# Install Python packages with retry mechanism
RUN ./install_packages.sh

# Copy the application
COPY . .

# Set environment variables for caching
ENV HF_HOME=/app/shared/cache
ENV TRANSFORMERS_CACHE=/app/shared/cache/transformers
ENV DIFFUSERS_CACHE=/app/shared/cache/diffusers

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]
