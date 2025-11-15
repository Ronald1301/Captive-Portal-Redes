#!/bin/bash
# Bloquea acceso saliente de la LAN hacia Internet excepto para el gateway
# y redirige tráfico HTTP/HTTPS al portal cautivo

# Detectar interfaces automáticamente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect_interfaces.sh" > /dev/null

if [ -z "$WAN_IF" ] || [ -z "$LAN_IF" ]; then
    echo "ERROR: No se pudieron detectar las interfaces de red"
    echo "Configúralas manualmente editando este script:"
    echo "  LAN_IF=\"tu_interfaz_lan\"  # ej: eth1, wlan0"
    echo "  WAN_IF=\"tu_interfaz_wan\"  # ej: eth0, enp3s0"
    exit 1
fi

# Limpiar reglas existentes
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

# Política por defecto: denegar forwarding
iptables -P FORWARD DROP
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT

# Permitir tráfico local en el gateway
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Permitir tráfico interno (estaciones a gateway)
iptables -A FORWARD -i $LAN_IF -o $LAN_IF -j ACCEPT

# Permitir conexiones establecidas/relacionadas
iptables -A FORWARD -i $LAN_IF -o $WAN_IF -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Permitir DNS al gateway (puerto 53)
iptables -A INPUT -i $LAN_IF -p udp --dport 53 -j ACCEPT
iptables -A INPUT -i $LAN_IF -p tcp --dport 53 -j ACCEPT

# Permitir HTTP/HTTPS al gateway (portal cautivo)
iptables -A INPUT -i $LAN_IF -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -i $LAN_IF -p tcp --dport 443 -j ACCEPT

# Detectar si existen certificados SSL para determinar puerto de redirección
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
if [ -f "$PROJECT_DIR/certs/server.crt" ] && [ -f "$PROJECT_DIR/certs/server.key" ]; then
    # Redirigir tráfico HTTP y HTTPS al puerto 443 (HTTPS)
    iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 80 -j DNAT --to-destination $LAN_IP:443
    iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 443 -j DNAT --to-destination $LAN_IP:443
    REDIRECT_PORT=443
    REDIRECT_PROTOCOL="HTTPS"
else
    # Redirigir tráfico HTTP y HTTPS al puerto 80 (HTTP)
    iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 80 -j DNAT --to-destination $LAN_IP:80
    iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 443 -j DNAT --to-destination $LAN_IP:80
    REDIRECT_PORT=80
    REDIRECT_PROTOCOL="HTTP"
fi

# Marcar conexiones desde LAN (para identificarlas después)
iptables -t mangle -A PREROUTING -i $LAN_IF -j MARK --set-mark 99

echo "✓ Internet bloqueado para hosts de LAN"
echo "✓ Tráfico HTTP/HTTPS redirigido al portal cautivo ($REDIRECT_PROTOCOL://$LAN_IP:$REDIRECT_PORT)"
echo "✓ Interfaces: LAN=$LAN_IF ($LAN_IP), WAN=$WAN_IF"
