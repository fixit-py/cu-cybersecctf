FROM ubuntu:20.04

# Install dependencies (including socat for networking)
RUN apt-get update && apt-get install -y \
    gcc \
    socat \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source and compile
COPY crackme.c /app/
RUN gcc -o crackme crackme.c

# Expose port
EXPOSE 3000

# Run socat to listen on port 3000 and execute the binary for each connection
ENTRYPOINT ["socat", "TCP-LISTEN:3000,reuseaddr,fork", "EXEC:/app/crackme"]
