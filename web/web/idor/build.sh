#!/bin/bash

# Build and run script for Auth Bypass Challenge
set -e

echo " Building Idor Challenge Docker Container..."

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down -v 2>/dev/null || true

# Build the Docker image
echo "🔨 Building Docker image..."
docker compose build --no-cache

# Start the services
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo ""
echo "To stop the challenge:"
echo "  docker compose down"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
