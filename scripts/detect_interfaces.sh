#!/bin/bash
# Script para detectar automáticamente interfaces LAN y WAN

detect_wan_interface() {
    # Detecta interfaz con gateway por defecto (conexión a Internet)
    local wan_if=$(ip route | grep default | awk '{print $5}' | head -n1)
    if [ -z "$wan_if" ]; then
        echo "ERROR: No se detectó interfaz WAN (sin gateway por defecto)" >&2
        return 1
    fi
    echo "$wan_if"
}

detect_lan_interface() {
    # Detecta interfaz(es) de red local (que no sea WAN ni loopback)
    local wan_if="$1"
    local lan_if=$(ip -o link show | awk -F': ' '{print $2}' | grep -v "^lo$" | grep -v "^$wan_if$" | head -n1)
    
    if [ -z "$lan_if" ]; then
        echo "ERROR: No se detectó interfaz LAN" >&2
        return 1
    fi
    echo "$lan_if"
}

get_interface_ip() {
    local iface="$1"
    ip -4 addr show "$iface" | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n1
}

# Detectar interfaces
WAN_IF=$(detect_wan_interface)
if [ $? -ne 0 ]; then
    exit 1
fi

LAN_IF=$(detect_lan_interface "$WAN_IF")
if [ $? -ne 0 ]; then
    exit 1
fi

# Obtener IPs
WAN_IP=$(get_interface_ip "$WAN_IF")
LAN_IP=$(get_interface_ip "$LAN_IF")

# Exportar para que otros scripts puedan usar
export WAN_IF
export LAN_IF
export WAN_IP
export LAN_IP

# Mostrar información
echo "=== Interfaces detectadas ===" >&2
echo "WAN: $WAN_IF (IP: ${WAN_IP:-sin IP})" >&2
echo "LAN: $LAN_IF (IP: ${LAN_IP:-sin IP})" >&2
echo "============================" >&2

# Output para sourcing
echo "WAN_IF=\"$WAN_IF\""
echo "LAN_IF=\"$LAN_IF\""
echo "WAN_IP=\"$WAN_IP\""
echo "LAN_IP=\"$LAN_IP\""
