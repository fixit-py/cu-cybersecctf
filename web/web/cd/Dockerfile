# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and tools that might be useful for the challenge
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY cd.py .
COPY .env .

# Create some files for the challenge
RUN echo "FLAG{command_injection_shipfast_pwned}" > /app/flag.txt && \
    echo "ShipFast Internal Documentation" > /app/internal_docs.txt && \
    echo "Database credentials: admin:super_secret_pass" >> /app/internal_docs.txt && \
    echo "API Keys stored in /etc/secrets/" >> /app/internal_docs.txt && \
    chmod 644 /app/flag.txt /app/internal_docs.txt

# Create non-root user for security but still allow command execution
RUN useradd -r -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 12700

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12700/ || exit 1

# Run the application
CMD ["python", "cd.py"]
