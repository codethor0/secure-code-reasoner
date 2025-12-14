FROM python:3.11-slim

LABEL maintainer="codethor0"
LABEL description="Secure Code Reasoner - A research-oriented toolkit for analyzing, fingerprinting, and reviewing code repositories"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install package
RUN pip install --no-cache-dir -e .

# Set entrypoint
ENTRYPOINT ["scr"]

# Default command
CMD ["--help"]

