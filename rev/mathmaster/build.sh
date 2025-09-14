#!/bin/bash

# Destroy existing containers and images
docker compose down --volumes --remove-orphans
docker system prune -f
docker rmi mathmaster 2>/dev/null || true

# Rebuild and bring up
docker compose build --no-cache
docker compose up -d
