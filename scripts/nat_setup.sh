#!/bin/bash
# Configura NAT (mascaramiento) en la interfaz WAN

# Detectar interfaz WAN automáticamente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect_interfaces.sh" > /dev/null

if [ -z "$WAN_IF" ]; then
  echo "ERROR: No se pudo detectar la interfaz WAN"
  echo "Configúrala manualmente: WAN_IF=\"tu_interfaz\" (ej: eth0, wlan0)"
  exit 1
fi

iptables -t nat -A POSTROUTING -o $WAN_IF -j MASQUERADE
echo "NAT configurado en $WAN_IF"
