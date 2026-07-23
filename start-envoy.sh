#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Path where Envoy expects the JWKS file
JWKS_FILE="/etc/envoy/jwks.json"
JWKS_DIR=$(dirname "$JWKS_FILE")

# The URL where the auth service exposes the JWKS.
# The 'auth' hostname is available from within the Docker network.
JWKS_URL="http://auth:5002/auth/jwks.json"

# Create the directory for the JWKS file if it doesn't exist
mkdir -p "$JWKS_DIR"

echo "Waiting for auth service to be available at $JWKS_URL..."

# Loop until the JWKS file is successfully downloaded.
# We use 'wget' with retry options to handle initial unavailability of the auth service.
wget --quiet --tries=10 --retry-connrefused --waitretry=5 -O "$JWKS_FILE" "$JWKS_URL"

echo "JWKS file downloaded successfully to $JWKS_FILE."

# Start Envoy with the original command
echo "Starting Envoy..."

# The original command from your docker-compose file
/usr/local/bin/envoy -c /etc/envoy/envoy.yaml --service-cluster specification-centralized-backend-cluster-dev