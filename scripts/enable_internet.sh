#!/bin/bash
# Habilita acceso a Internet para una IP concreta mediante iptables
# Uso: enable_internet.sh <IP>

IP="$1"
if [ -z "$IP" ]; then
  echo "Usage: $0 <IP>"
  exit 1
fi

# Detectar interfaces automáticamente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect_interfaces.sh" > /dev/null 2>&1

if [ -z "$WAN_IF" ] || [ -z "$LAN_IF" ]; then
    echo "ERROR: No se pudieron detectar las interfaces. Usando valores por defecto."
    LAN_IF="eth1"
    WAN_IF="eth0"
fi

# Verificar si la IP ya tiene acceso
if iptables -C FORWARD -s $IP -i $LAN_IF -o $WAN_IF -j ACCEPT 2>/dev/null; then
    echo "⚠ La IP $IP ya tiene acceso a Internet"
    exit 0
fi

# Permitir forwarding bidireccional para la IP autenticada
iptables -I FORWARD 1 -s $IP -i $LAN_IF -o $WAN_IF -j ACCEPT
iptables -I FORWARD 1 -d $IP -i $WAN_IF -o $LAN_IF -m state --state ESTABLISHED,RELATED -j ACCEPT

# Excluir esta IP de la redirección NAT al portal (ya está autenticada)
iptables -t nat -I PREROUTING 1 -i $LAN_IF -s $IP -p tcp --dport 80 -j ACCEPT
iptables -t nat -I PREROUTING 1 -i $LAN_IF -s $IP -p tcp --dport 443 -j ACCEPT

echo "✓ Acceso a Internet habilitado para $IP"
