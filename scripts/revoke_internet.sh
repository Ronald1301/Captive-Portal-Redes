#!/bin/bash
# Script para revocar acceso a Internet de una IP específica
# Útil para cerrar sesiones o cuando un usuario se desconecta
# Uso: revoke_internet.sh <IP>

IP="$1"
if [ -z "$IP" ]; then
  echo "Usage: $0 <IP>"
  exit 1
fi

# Detectar interfaces automáticamente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect_interfaces.sh" > /dev/null 2>&1

if [ -z "$WAN_IF" ] || [ -z "$LAN_IF" ]; then
    echo "ERROR: No se pudieron detectar las interfaces."
    exit 1
fi

# Eliminar reglas de forwarding para esta IP
iptables -D FORWARD -s $IP -i $LAN_IF -o $WAN_IF -j ACCEPT 2>/dev/null
iptables -D FORWARD -d $IP -i $WAN_IF -o $LAN_IF -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null

# Eliminar excepciones de redirección NAT
iptables -t nat -D PREROUTING -i $LAN_IF -s $IP -p tcp --dport 80 -j ACCEPT 2>/dev/null
iptables -t nat -D PREROUTING -i $LAN_IF -s $IP -p tcp --dport 443 -j ACCEPT 2>/dev/null

echo "✓ Acceso a Internet revocado para $IP"
