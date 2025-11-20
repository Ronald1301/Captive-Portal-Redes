#!/bin/bash
# Script de inicialización completa del portal cautivo
# Configura NAT, bloquea internet, inicia DNS y servidor web

set -e  # Salir si hay algún error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "   PORTAL CAUTIVO - Inicialización"
echo "========================================="
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ ERROR: Este script debe ejecutarse como root"
    echo "   Ejecuta: sudo $0"
    exit 1
fi

# Verificar dependencias
if ! command -v iptables &> /dev/null; then
    echo "❌ ERROR: iptables no está instalado"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 no está instalado"
    exit 1
fi

echo "1. Detectando interfaces de red..."
source "$SCRIPT_DIR/detect_interfaces.sh"

if [ -z "$WAN_IF" ] || [ -z "$LAN_IF" ]; then
    echo "❌ ERROR: No se pudieron detectar las interfaces de red"
    exit 1
fi

echo "   ✓ WAN: $WAN_IF ($WAN_IP)"
echo "   ✓ LAN: $LAN_IF ($LAN_IP)"
echo ""

# Habilitar IP forwarding
echo "2. Habilitando IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1 > /dev/null
echo "   ✓ IP forwarding habilitado"
echo ""

# Configurar NAT
echo "3. Configurando NAT (masquerading)..."
bash "$SCRIPT_DIR/nat_setup.sh"
echo ""

# Bloquear internet y configurar redirecciones
echo "4. Bloqueando internet y configurando redirecciones..."
bash "$SCRIPT_DIR/disable_internet.sh"
echo ""

# Crear archivo PID para tracking de procesos
PID_FILE="/var/run/captive-portal.pid"

# Función para limpiar al salir
cleanup() {
    echo ""
    echo "========================================="
    echo "   Deteniendo Portal Cautivo..."
    echo "========================================="
    
    if [ -f "$PID_FILE" ]; then
        while IFS= read -r pid; do
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "Matando proceso $pid"
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    echo "✓ Procesos detenidos"
    echo ""
    echo "NOTA: Las reglas de iptables permanecen activas."
    echo "Para restaurar el acceso a internet, ejecuta:"
    echo "  sudo iptables -F"
    echo "  sudo iptables -t nat -F"
}

trap cleanup EXIT INT TERM

# Iniciar servidor DNS
echo "5. Iniciando servidor DNS falso (puerto 53)..."
python3 "$PROJECT_DIR/dns_server.py" --ip $LAN_IP > /dev/null 2>&1 &
DNS_PID=$!
echo $DNS_PID > "$PID_FILE"
sleep 1

if ps -p $DNS_PID > /dev/null; then
    echo "   ✓ Servidor DNS iniciado (PID: $DNS_PID)"
else
    echo "   ❌ ERROR: No se pudo iniciar el servidor DNS"
    exit 1
fi
echo ""

# Iniciar servidor web
echo "6. Iniciando servidor web del portal (puerto 80)..."
cd "$PROJECT_DIR"
python3 server.py --host 0.0.0.0 --port 80 > /dev/null 2>&1 &
WEB_PID=$!
echo $WEB_PID >> "$PID_FILE"
sleep 1

if ps -p $WEB_PID > /dev/null; then
    echo "   ✓ Servidor web iniciado (PID: $WEB_PID)"
else
    echo "   ❌ ERROR: No se pudo iniciar el servidor web"
    exit 1
fi
echo ""

echo "========================================="
echo "   ✓ PORTAL CAUTIVO ACTIVO"
echo "========================================="
echo ""
echo "Configuración:"
echo "  • Gateway IP: $LAN_IP"
echo "  • Interfaz LAN: $LAN_IF"
echo "  • Interfaz WAN: $WAN_IF"
echo "  • Puerto web: 80"
echo "  • Puerto DNS: 53"
echo ""
echo "Los dispositivos en la red deben configurar:"
echo "  • Gateway: $LAN_IP"
echo "  • DNS: $LAN_IP"
echo ""
echo "Logs en tiempo real:"
echo "  • DNS: ps -f -p $DNS_PID"
echo "  • Web: ps -f -p $WEB_PID"
echo ""
echo "Presiona Ctrl+C para detener el portal"
echo "========================================="
echo ""

# Mantener el script corriendo
wait
