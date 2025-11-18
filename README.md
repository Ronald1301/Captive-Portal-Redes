# Portal Cautivo - Proyecto Redes 2025

Sistema completo de portal cautivo que bloquea el acceso a internet hasta que los usuarios se autentiquen. Implementado en Python con biblioteca estándar y scripts bash para Linux.

## 🎯 Características Principales

- ✅ **Bloqueo automático de internet** para todos los dispositivos en la red
- ✅ **Servidor DNS falso** que redirige todo el tráfico al portal
- ✅ **Redirección HTTP/HTTPS** automática al portal de login
- ✅ **Control por IP** - acceso individual después de autenticación
- ✅ **Gateway/Router funcional** para dispositivos en la red
- ✅ **Servidor web multihilo** con gestión de sesiones
- ✅ **Sin bibliotecas externas** - solo Python estándar y bash
- 🔐 **Seguridad robusta** - CSRF, rate limiting, hashing seguro, logging
- 🔐 **Protección anti-fuerza bruta** - bloqueo automático después de 5 intentos
- 🔐 **Tokens seguros** - tokens de sesión y CSRF criptográficamente seguros
- 🔐 **Timeout de sesiones** - expiran automáticamente después de 1 hora

## 📁 Estructura del Proyecto

```
├── server.py              # Servidor web HTTP del portal (implementación con sockets)
├── dns_server.py          # Servidor DNS falso para redirección
├── auth.py               # Sistema de autenticación con hashing seguro
├── users.json            # Base de datos de usuarios
├── logs/                 # Directorio de logs de seguridad
│   └── security.log     # Eventos de seguridad registrados
├── templates/            # Páginas HTML del portal
│   ├── index.html       # Página de login
│   └── success.html     # Página de éxito
└── scripts/             # Scripts de configuración
    ├── start_captive_portal.sh    # ⭐ Inicia todo el sistema
    ├── stop_captive_portal.sh     # Detiene el portal
    ├── enable_internet.sh         # Habilita internet para una IP
    ├── revoke_internet.sh         # Revoca acceso de una IP
    ├── disable_internet.sh        # Bloquea internet (llamado por start)
    ├── nat_setup.sh              # Configura NAT (llamado por start)
    └── detect_interfaces.sh      # Detecta interfaces LAN/WAN
```

## 🚀 Inicio Rápido

### Requisitos Previos

- Sistema Linux (Ubuntu, Debian, CentOS, etc.)
- Python 3.6 o superior
- iptables instalado
- Acceso root/sudo
- **Dos interfaces de red**: una para LAN (dispositivos locales) y otra para WAN (internet)

### Instalación y Uso

1. **Dar permisos de ejecución a los scripts:**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Verificar detección de interfaces (opcional):**
   ```bash
   ./scripts/test_detection.sh
   ```
   Esto mostrará qué interfaces LAN y WAN fueron detectadas automáticamente.

3. **Iniciar el portal cautivo:**
   ```bash
   sudo ./scripts/start_captive_portal.sh
   ```
   
   Este script hace TODO automáticamente:
   - ✓ Habilita IP forwarding
   - ✓ Configura NAT/masquerading
   - ✓ Bloquea internet para todos
   - ✓ Configura redirección HTTP/HTTPS al portal
   - ✓ Inicia servidor DNS (puerto 53)
   - ✓ Inicia servidor web (puerto 80)

4. **Configurar dispositivos cliente:**
   
   En cada dispositivo que quiera conectarse:
   - **Gateway:** IP del servidor (ej: 192.168.1.1)
   - **DNS:** IP del servidor (ej: 192.168.1.1)
   - Puedes hacerlo manual o configurar un servidor DHCP

5. **Probar el portal:**
   - Abre un navegador en cualquier dispositivo cliente
   - Intenta acceder a cualquier página web (ej: google.com)
   - Serás redirigido automáticamente al portal de login
   - Usa las credenciales de `users.json` para autenticarte

6. **Detener el portal:**
   ```bash
   sudo ./scripts/stop_captive_portal.sh
   ```

## 👥 Gestión de Usuarios

### Método 1: Usando la utilidad de línea de comandos (Recomendado)

```bash
# Agregar nuevo usuario con hash seguro
python3 auth.py add username password

# Actualizar contraseña de usuario existente
python3 auth.py update username nueva_password

# Listar todos los usuarios
python3 auth.py list
```

### Método 2: Editar manualmente

El archivo `users.json` contiene las cuentas de usuario:

```json
{
  "users": [
    {
      "username": "admin",
      "password": "pbkdf2:sha256:10000:a1b2c3...:d4e5f6..."
    },
    {
      "username": "user1",
      "password": "pbkdf2:sha256:10000:x7y8z9...:k1l2m3..."
    }
  ]
}
```

**Nota:** Las contraseñas ahora usan hashing seguro con salt. Para testing rápido, puedes usar texto plano, pero NO es recomendado.

## 🔐 Características de Seguridad

Este portal incluye múltiples capas de seguridad (ver `SEGURIDAD.md` para detalles completos):

### Protección CSRF
- Tokens únicos por formulario
- Validación estricta por IP
- Expiración automática de tokens

### Rate Limiting
- Máximo 5 intentos de login
- Bloqueo automático de 5 minutos
- Tracking por dirección IP

### Hashing Seguro de Contraseñas
- Algoritmo: SHA-256 con salt
- 10,000 iteraciones (PBKDF2-like)
- Salt único por contraseña
- Protección contra timing attacks

### Gestión de Sesiones
- Tokens criptográficamente seguros
- Timeout automático (1 hora)
- Cookies con HttpOnly y SameSite
- Limpieza automática de sesiones expiradas

### Logging de Seguridad
- Todos los eventos se registran en `logs/security.log`
- Tracking de intentos fallidos
- Alertas de actividad sospechosa
- Útil para auditorías

```bash
# Ver logs de seguridad en tiempo real
tail -f logs/security.log

# Buscar IPs bloqueadas
grep "IP_BLOCKED" logs/security.log

# Ver intentos fallidos
grep "LOGIN_FAILED" logs/security.log
```

## 🔧 Configuración Avanzada

### Interfaces de Red Manuales

Si la detección automática falla, edita `scripts/detect_interfaces.sh` y configura:

```bash
WAN_IF="eth0"    # Tu interfaz con internet
LAN_IF="eth1"    # Tu interfaz de red local
```

### Soporte HTTPS

Para usar HTTPS en el portal:

```bash
# Generar certificado autofirmado
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365

# Iniciar con HTTPS (puerto 443)
sudo python3 server.py --host 0.0.0.0 --port 443 --cert cert.pem --key key.pem
```

### Comandos Útiles

```bash
# Ver reglas de iptables activas
sudo iptables -L -n -v
sudo iptables -t nat -L -n -v

# Ver dispositivos conectados (ARP)
arp -a

# Habilitar internet manualmente para una IP
sudo ./scripts/enable_internet.sh 192.168.1.100

# Revocar acceso de una IP
sudo ./scripts/revoke_internet.sh 192.168.1.100

# Ver procesos del portal
cat /var/run/captive-portal.pid
```

## 🔍 Cómo Funciona

1. **DNS Hijacking**: El servidor DNS falso responde a todas las consultas con la IP del gateway
2. **HTTP Redirection**: iptables redirige todo el tráfico HTTP/HTTPS al puerto 80 del servidor
3. **Autenticación**: Los usuarios se autentican en la página web
4. **Firewall Control**: Después del login, se crean reglas de iptables específicas para permitir el forwarding de esa IP
5. **NAT/Masquerading**: El tráfico autorizado pasa por NAT hacia internet

### Flujo de Conexión

```
Cliente intenta google.com
    ↓
DNS query → DNS Server (falso) → Responde con IP del gateway
    ↓
HTTP request → iptables redirect → Portal cautivo (puerto 80)
    ↓
Usuario se loguea
    ↓
Script enable_internet.sh crea regla de forwarding
    ↓
Cliente tiene acceso a internet
```

## 🛡️ Seguridad

### Implementado:
- Validación de credenciales
- Control por IP individual
- Verificación de MAC address (básica)
- Gestión de sesiones con cookies

### Limitaciones (proyecto académico):
- ⚠️ Contraseñas en texto plano (para demo)
- ⚠️ Sin protección CSRF
- ⚠️ Sesiones en memoria (no persistentes)
- ⚠️ Sin protección contra ARP spoofing avanzado

### Para Producción:
- Usar hashing con sal (bcrypt, argon2)
- Implementar HTTPS obligatorio
- Agregar rate limiting
- Persistencia de sesiones en base de datos
- Logging completo de accesos
- Protección contra ARP spoofing

## 🧪 Pruebas y Debugging

```bash
# Ver logs en tiempo real del servidor web
sudo tail -f /var/log/syslog | grep python3

# Verificar que DNS está escuchando
sudo netstat -tulpn | grep :53

# Verificar que el servidor web está escuchando
sudo netstat -tulpn | grep :80

# Test de conectividad desde cliente
ping <IP_del_gateway>
nslookup google.com <IP_del_gateway>
```

## 📝 Requisitos del Proyecto Cumplidos

- ✅ Endpoint HTTP de inicio de sesión
- ✅ Bloqueo de enrutamiento hasta inicio de sesión
- ✅ Gestión de cuentas de usuario
- ✅ Concurrencia usando hilos
- ✅ Scripts de iptables para control de acceso
- ✅ NAT/masquerading configurado
- ✅ Detección automática de interfaces
- ✅ Servidor DNS para redirección
- ✅ Redirección automática de tráfico HTTP/HTTPS

## 🐛 Solución de Problemas

**Problema:** No se detectan las interfaces
- Solución: Ejecuta `ip addr` y configura manualmente en `detect_interfaces.sh`

**Problema:** Los clientes no son redirigidos al portal
- Verifica que el DNS del cliente apunta al gateway
- Verifica que las reglas de iptables están activas: `sudo iptables -t nat -L -n`

**Problema:** Después del login no hay internet
- Verifica que NAT está configurado: `sudo iptables -t nat -L -n | grep MASQUERADE`
- Verifica IP forwarding: `cat /proc/sys/net/ipv4/ip_forward` (debe ser 1)

**Problema:** "Permission denied" al iniciar
- Todos los scripts deben ejecutarse con `sudo`
- Verifica permisos: `chmod +x scripts/*.sh`

## 📚 Referencias Técnicas

- iptables: Control de firewall y NAT en Linux
- NAT (Network Address Translation): Permite que múltiples dispositivos compartan una conexión
- DNS (Domain Name System): Resuelve nombres de dominio a direcciones IP
- HTTP Redirect: Técnica para redirigir peticiones web

## 👨‍💻 Desarrollo

Este es un proyecto académico para el curso de Redes 2025. Implementa un portal cautivo funcional usando solo la biblioteca estándar de Python y herramientas nativas de Linux.

**No usa bibliotecas externas** - Todo está implementado con:
- Python 3 (biblioteca estándar)
- Bash scripting
- iptables
- Herramientas de red estándar de Linux

---

**Nota:** Este proyecto está diseñado para fines educativos. Para uso en producción, se requieren mejoras adicionales de seguridad y robustez.
