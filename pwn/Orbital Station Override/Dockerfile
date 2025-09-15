FROM ubuntu:latest
WORKDIR /app

# Install 32-bit library support and socat
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y socat libc6:i386 && \
    rm -rf /var/lib/apt/lists/*

COPY ./mine_challenge ./mine_challenge
COPY ./flag.txt ./flag.txt
RUN chmod +x ./mine_challenge

# Ensure the binary has the flag file in the same directory
EXPOSE 9300
CMD ["socat", "TCP-LISTEN:9300,fork,reuseaddr", "EXEC:./mine_challenge"]
