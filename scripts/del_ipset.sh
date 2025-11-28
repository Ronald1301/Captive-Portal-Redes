#!/bin/bash
# scripts/del_ipset.sh
# Elimina una IP del set de ipset de autenticados

set -e

SET_NAME="authed_ips"
IP="$1"

if [ -z "$IP" ]; then
    echo "Uso: $0 <IP>"
    exit 1
fi

ipset del "$SET_NAME" "$IP" || true
