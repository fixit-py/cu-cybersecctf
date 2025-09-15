FROM ubuntu:latest AS app
WORKDIR /app/

# Just copy the files without recompiling
COPY ./neural.c /app/neural.c
COPY ./neural /app/neural
COPY ./flag.txt /app/flag.txt

FROM ubuntu:latest

# Install 32-bit runtime libraries for dynamic linking
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y \
    libc6:i386 \
    libgcc-s1:i386 \
    socat \
    && rm -rf /var/lib/apt/lists/*

# Copy files from build stage
COPY --from=app /app /srv/app
COPY --chmod=555 ./run /srv/app/run

# Create jail-like environment
RUN useradd -m -s /bin/bash ctf && \
    chown -R ctf:ctf /srv/app

WORKDIR /srv/app
EXPOSE 19000

# Use socat to provide the service
CMD ["socat", "TCP-LISTEN:19000,fork,reuseaddr", "EXEC:/srv/app/run,pty,stderr"]
