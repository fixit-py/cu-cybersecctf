FROM ubuntu:20.04

# Install GCC and socat for the challenge
RUN apt-get update && apt-get install -y gcc socat && rm -rf /var/lib/apt/lists/*

# Set up the challenge directory
WORKDIR /app

# Copy the source code
COPY mathmaster.c .

# Compile the binary (unstripped for easier reversing)
RUN gcc -o mathmaster mathmaster.c

# Expose the port for the challenge
EXPOSE 9999

# Run socat to listen on port 9999 and pipe input/output to the binary
ENTRYPOINT ["socat", "TCP-LISTEN:9999,reuseaddr,fork", "EXEC:./mathmaster"]
