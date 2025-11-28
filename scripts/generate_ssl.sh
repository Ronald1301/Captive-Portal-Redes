#!/bin/bash
# scripts/generate_ssl.sh
# Genera certificados autofirmados para HTTPS del portal cautivo

set -e

CERT_DIR="$(dirname "$0")/../certs"
mkdir -p "$CERT_DIR"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$CERT_DIR/portal.key" \
    -out "$CERT_DIR/portal.crt" \
    -subj "/C=XX/ST=Captive/L=Portal/O=CaptivePortal/OU=IT/CN=portal.local"

echo "Certificados generados en $CERT_DIR"
