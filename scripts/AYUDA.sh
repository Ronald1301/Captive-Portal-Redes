#!/bin/bash
# Script de ayuda rápida - Muestra información útil

cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║          PORTAL CAUTIVO - Ayuda Rápida                   ║
╚═══════════════════════════════════════════════════════════╝

📖 DOCUMENTACIÓN:
   docs/RESUMEN-CONFIGURACION.md          ← EMPIEZA AQUÍ
   docs/GUIA-RAPIDA-PRUEBA-TELEFONO.md    ← Pasos rápidos
   docs/CONFIGURACION-ESCENARIO-TELEFONO.md ← Detalles completos
   docs/06-CONFIGURACION-PRUEBAS-VIRTUALBOX.md ← Portal completo

🚀 SCRIPTS DISPONIBLES:

   1. MODO DEMOSTRACIÓN (1 interfaz):
      sudo ./scripts/check_network.sh     # Verificar red
      sudo ./scripts/demo_mode.sh         # Ejecutar portal

   2. MODO COMPLETO (2 interfaces):
      sudo ./scripts/start_captive_portal.sh  # Iniciar
      sudo ./scripts/stop_captive_portal.sh   # Detener

   3. GESTIÓN DE ACCESO:
      sudo ./scripts/enable_internet.sh <IP>  # Habilitar
      sudo ./scripts/revoke_internet.sh <IP>  # Revocar

👥 GESTIÓN DE USUARIOS:
   python3 auth.py add <usuario> <contraseña>
   python3 auth.py update <usuario> <nueva_contraseña>
   python3 auth.py list

🎯 TU ESCENARIO (Teléfono + Laptop + VM):
   1. Teléfono con hotspot (192.168.43.1)
   2. Laptop Windows conectada al hotspot
   3. VM Ubuntu en VirtualBox (modo bridge)
   4. IP de la VM: 192.168.43.100

📱 PARA PROBAR:
   • Desde navegador: http://192.168.43.100
   • Usuario: admin
   • Contraseña: admin123

⚠️  MODO DEMOSTRACIÓN:
   ✅ Servidor web funcional
   ✅ Sistema de login
   ❌ NO bloquea internet automáticamente
   
   Para portal completo → Ver docs/CONFIGURACION-ESCENARIO-TELEFONO.md

🐛 PROBLEMAS COMUNES:

   "No puedo acceder al portal"
   → Verifica IP de la VM: ip addr show
   → Verifica servidor: sudo netstat -tuln | grep :80
   → Verifica ping: ping 192.168.43.100

   "Permission denied"
   → Ejecuta con sudo
   → Verifica permisos: chmod +x scripts/*.sh

   "Address already in use"
   → Otro servicio usa el puerto 80
   → Detener Apache: sudo systemctl stop apache2
   → Detener Nginx: sudo systemctl stop nginx

   "Sin internet en la VM"
   → Verifica gateway: ip route show
   → Verifica DNS: nslookup google.com
   → Verifica conexión: ping 8.8.8.8

🔧 CONFIGURACIÓN RÁPIDA (VM Ubuntu):

   # 1. IP estática
   sudo nano /etc/netplan/01-netcfg.yaml

   network:
     version: 2
     renderer: networkd
     ethernets:
       enp0s3:  # Tu interfaz
         dhcp4: no
         addresses:
           - 192.168.43.100/24
         routes:
           - to: default
             via: 192.168.43.1
         nameservers:
           addresses:
             - 8.8.8.8
             - 8.8.4.4

   sudo netplan apply

   # 2. Verificar
   ping 8.8.8.8

   # 3. Ejecutar portal
   sudo ./scripts/demo_mode.sh

📞 PARA MÁS AYUDA:
   Lee: docs/RESUMEN-CONFIGURACION.md

╚═══════════════════════════════════════════════════════════╝
EOF
