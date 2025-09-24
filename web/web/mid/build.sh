#!/bin/bash

set -e

echo "Building Docker Container..."

echo "Cleaning up existing containers..."
docker compose down -v 2>/dev/null || true

echo "Building Docker image..."
docker compose build --no-cache

echo "Starting services..."
docker compose up -d
