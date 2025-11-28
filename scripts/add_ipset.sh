#!/bin/bash
# scripts/add_ipset.sh
# Agrega una IP autenticada al set de ipset con expiración automática

set -e

SET_NAME="authed_ips"
IP="$1"
TIMEOUT=3600  # 1 hora

if [ -z "$IP" ]; then
    echo "Uso: $0 <IP>"
    exit 1
fi

ipset add "$SET_NAME" "$IP" timeout $TIMEOUT || true
