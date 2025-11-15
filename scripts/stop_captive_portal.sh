#!/bin/bash
# Script para detener el portal cautivo y limpiar reglas

echo "Deteniendo portal cautivo..."

# Detener procesos
PID_FILE="/var/run/captive-portal.pid"
if [ -f "$PID_FILE" ]; then
    while IFS= read -r pid; do
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Deteniendo proceso $pid"
            kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    echo "✓ Procesos detenidos"
else
    echo "⚠ No se encontró archivo PID, buscando procesos..."
    # Buscar y matar procesos por nombre
    pkill -f "dns_server.py" 2>/dev/null
    pkill -f "server.py.*--port 80" 2>/dev/null
fi

# Preguntar si limpiar reglas de iptables
read -p "¿Limpiar reglas de iptables? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "Limpiando reglas de iptables..."
    iptables -F
    iptables -t nat -F
    iptables -t mangle -F
    iptables -X
    iptables -P INPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -P OUTPUT ACCEPT
    echo "✓ Reglas de iptables limpiadas"
else
    echo "⚠ Reglas de iptables conservadas"
    echo "  Para limpiarlas manualmente:"
    echo "    sudo iptables -F"
    echo "    sudo iptables -t nat -F"
fi

echo ""
echo "✓ Portal cautivo detenido"
