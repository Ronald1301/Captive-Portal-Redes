#!/bin/bash
# Script para verificar la configuración de red antes de ejecutar el portal
# Útil para diagnosticar problemas de conectividad

echo "========================================="
echo "   Diagnóstico de Red - Portal Cautivo"
echo "========================================="
echo ""

# Función para verificar comandos
check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1 está instalado"
        return 0
    else
        echo "❌ $1 NO está instalado"
        return 1
    fi
}

# 1. Verificar comandos necesarios
echo "1️⃣  Verificando herramientas necesarias..."
check_command "ip"
check_command "ping"
check_command "python3"
check_command "iptables"
echo ""

# 2. Mostrar interfaces de red
echo "2️⃣  Interfaces de red disponibles:"
ip -brief addr show
echo ""

# 3. Detectar IP principal
echo "3️⃣  Dirección IP principal:"
MAIN_IP=$(hostname -I | awk '{print $1}')
if [ -n "$MAIN_IP" ]; then
    echo "   IP: $MAIN_IP"
else
    echo "   ⚠️  No se detectó ninguna IP"
fi
echo ""

# 4. Verificar gateway
echo "4️⃣  Gateway predeterminado:"
GATEWAY=$(ip route | grep default | awk '{print $3}')
if [ -n "$GATEWAY" ]; then
    echo "   Gateway: $GATEWAY"
    
    # Hacer ping al gateway
    echo "   Probando conectividad al gateway..."
    if ping -c 2 -W 2 $GATEWAY > /dev/null 2>&1; then
        echo "   ✅ Gateway accesible"
    else
        echo "   ⚠️  Gateway no responde"
    fi
else
    echo "   ⚠️  No se detectó gateway"
fi
echo ""

# 5. Verificar DNS
echo "5️⃣  Resolución DNS:"
echo "   Probando conectividad a 8.8.8.8..."
if ping -c 2 -W 2 8.8.8.8 > /dev/null 2>&1; then
    echo "   ✅ Conectividad a internet OK"
else
    echo "   ⚠️  Sin conectividad a internet"
fi
echo ""

# 6. Verificar puertos
echo "6️⃣  Verificando puertos del portal:"
if command -v netstat &> /dev/null; then
    echo "   Puertos en escucha:"
    netstat -tuln | grep -E ':(80|443|53) ' || echo "   (Ningún puerto del portal en escucha)"
elif command -v ss &> /dev/null; then
    echo "   Puertos en escucha:"
    ss -tuln | grep -E ':(80|443|53) ' || echo "   (Ningún puerto del portal en escucha)"
else
    echo "   ⚠️  No se puede verificar puertos (netstat/ss no disponible)"
fi
echo ""

# 7. Verificar archivos del proyecto
echo "7️⃣  Verificando archivos del proyecto:"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

FILES=("server.py" "auth.py" "users.json" "templates/index.html" "templates/success.html")

for file in "${FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (FALTA)"
    fi
done
echo ""

# 8. Verificar permisos
echo "8️⃣  Verificando permisos:"
if [ "$EUID" -eq 0 ]; then
    echo "   ✅ Ejecutando como root"
else
    echo "   ⚠️  No ejecutando como root (algunos comandos pueden fallar)"
fi
echo ""

# 9. Verificar reglas de iptables actuales
echo "9️⃣  Reglas de iptables actuales:"
if [ "$EUID" -eq 0 ]; then
    FORWARD_RULES=$(iptables -L FORWARD -n | wc -l)
    NAT_RULES=$(iptables -t nat -L -n | wc -l)
    echo "   Reglas FORWARD: $FORWARD_RULES"
    echo "   Reglas NAT: $NAT_RULES"
    
    if [ $FORWARD_RULES -gt 3 ] || [ $NAT_RULES -gt 10 ]; then
        echo "   ⚠️  Hay reglas de iptables configuradas"
        echo "      (Puede ser de una ejecución anterior)"
    fi
else
    echo "   ⚠️  Requiere root para verificar iptables"
fi
echo ""

# 10. Resumen y recomendaciones
echo "========================================="
echo "   RESUMEN Y RECOMENDACIONES"
echo "========================================="
echo ""

if [ -n "$MAIN_IP" ] && [ -n "$GATEWAY" ] && ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
    echo "✅ Configuración de red básica: OK"
    echo ""
    echo "📱 Para MODO DEMOSTRACIÓN, ejecuta:"
    echo "   sudo $SCRIPT_DIR/demo_mode.sh"
    echo ""
    echo "   Los dispositivos podrán acceder al portal en:"
    echo "   http://$MAIN_IP"
    echo ""
    echo "🔥 Para PORTAL CAUTIVO COMPLETO, necesitas:"
    echo "   • 2 interfaces de red en la VM"
    echo "   • Consultar: docs/CONFIGURACION-ESCENARIO-TELEFONO.md"
else
    echo "⚠️  PROBLEMAS DETECTADOS:"
    echo ""
    
    if [ -z "$MAIN_IP" ]; then
        echo "   • No hay dirección IP configurada"
        echo "     → Verifica tu configuración de red"
    fi
    
    if [ -z "$GATEWAY" ]; then
        echo "   • No hay gateway configurado"
        echo "     → Verifica tu configuración de red"
    fi
    
    if ! ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
        echo "   • Sin conectividad a internet"
        echo "     → Verifica tu conexión al hotspot del teléfono"
    fi
    
    echo ""
    echo "Soluciona estos problemas antes de ejecutar el portal."
fi

echo ""
echo "========================================="
