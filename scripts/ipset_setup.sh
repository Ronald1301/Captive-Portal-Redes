#!/bin/bash
# scripts/ipset_setup.sh
# Inicializa el set de IPs autenticadas para el portal cautivo

set -e

# Nombre del set
SET_NAME="authed_ips"

# Crear el set si no existe
if ! ipset list "$SET_NAME" &>/dev/null; then
    ipset create "$SET_NAME" hash:ip timeout 3600
fi

echo "Set de IPs autenticadas listo: $SET_NAME"
