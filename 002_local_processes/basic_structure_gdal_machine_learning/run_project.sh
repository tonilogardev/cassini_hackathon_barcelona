#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "============================================="
echo "   Starting antigravity-geo-ml Environment   "
echo "============================================="

# Ensure script is run from project root
cd "$(dirname "$0")"

# Build the Docker image using BuildKit
echo "-> Building Docker image with BuildKit..."
export DOCKER_BUILDKIT=1
docker compose build

# Run the default CLI command (help) to verify setup
echo "-> Running initial CLI verification..."
docker compose run --rm cli --help

echo "============================================="
echo "   Environment Ready!                        "
echo "   Use 'docker compose run --rm cli <cmd>'   "
echo "   to execute your tasks.                    "
echo "============================================="
