FROM python:3.11-slim@sha256:158caf0e080e2cd74ef2879ed3c4e697792ee65251c8208b7afb56683c32ea6c

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

# Create non-root user
RUN addgroup --system scr && adduser --system --ingroup scr scr

# Set ownership of application directory
RUN chown -R scr:scr /app

# Switch to non-root user
USER scr

# Set entrypoint
ENTRYPOINT ["scr"]

# Default command
CMD ["--help"]

