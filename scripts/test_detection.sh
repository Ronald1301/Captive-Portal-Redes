#!/bin/bash
# Script de prueba para verificar la detección automática de interfaces

echo "=== Probando detección automática de interfaces ==="
echo ""

# Ejecutar script de detección
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/detect_interfaces.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Detección exitosa"
    echo ""
    echo "Interfaces que se usarán en los scripts:"
    echo "  - WAN (Internet): $WAN_IF (IP: $WAN_IP)"
    echo "  - LAN (Red local): $LAN_IF (IP: $LAN_IP)"
    echo ""
    echo "Si estas interfaces son correctas, puedes proceder con:"
    echo "  sudo ./nat_setup.sh"
    echo "  sudo ./disable_internet.sh"
    echo "  sudo python3 ../server.py"
else
    echo ""
    echo "✗ Error en la detección"
    echo ""
    echo "Verifica tu configuración de red con:"
    echo "  ip addr        # Ver todas las interfaces"
    echo "  ip route       # Ver gateway por defecto"
    exit 1
fi
