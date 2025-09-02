# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Redis
RUN apt-get update && apt-get install -y \
    curl \
    redis-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY user_enum_app.py .
COPY .env .

# Create supervisor configuration for Redis and Flask
RUN echo '[supervisord]\n\
nodaemon=true\n\
user=root\n\
\n\
[program:redis]\n\
command=redis-server --bind 0.0.0.0 --port 6379\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/var/log/redis.log\n\
stderr_logfile=/var/log/redis.log\n\
\n\
[program:flask]\n\
command=python user_enum_app.py\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/var/log/flask.log\n\
stderr_logfile=/var/log/flask.log' > /etc/supervisor/conf.d/supervisord.conf

# Create log directory
RUN mkdir -p /var/log

# Expose port
EXPOSE 17800

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:17800/ || exit 1

# Run supervisor to manage both Redis and Flask
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
