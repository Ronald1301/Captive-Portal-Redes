# 🌐 Portal Cautivo - Proyecto Redes 2025

Sistema de portal cautivo completo que controla el acceso a internet hasta que los usuarios se autentiquen. Implementado desde cero con Python (stdlib) y bash para Linux.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux-green.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Grade-7.5%2F5.0-brightgreen.svg" alt="Grade">
</p>

---

## ✨ Características

### 📋 Requisitos Mínimos (5.0 puntos)
- ✅ **Servidor HTTP manual** - Implementado con sockets puros (sin `http.server`)
- ✅ **Bloqueo de internet** - iptables con política DROP hasta autenticación
- ✅ **Sistema de usuarios** - CLI + JSON + hashing SHA-256
- ✅ **Concurrencia** - Threading para múltiples clientes simultáneos

### 🌟 Extras Implementados (2.5 puntos)
- ✅ **[1.0 pto] Detección automática** - DNS falso + notificaciones en dispositivos
- ✅ **[0.5 pto] HTTPS/SSL** - Conexiones cifradas con TLS
- ✅ **[0.5 pto] Anti-suplantación** - Verificación IP + MAC address
- ✅ **[0.25 pto] NAT/Masquerading** - Enmascaramiento de IPs
- ✅ **[0.25 pto] Diseño moderno** - UI profesional con gradientes y efectos

**📊 Puntuación Total: 7.5/5.0** 🏆

---

## 🚀 Inicio Rápido

### Requisitos
- Linux (Ubuntu/Debian/CentOS)
- Python 3.6+
- iptables
- Dos interfaces de red (LAN + WAN)

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/captive-portal.git
cd captive-portal

# 2. Dar permisos de ejecución
chmod +x scripts/*.sh
chmod +x generate_cert.sh

# 3. [OPCIONAL] Generar certificados SSL para HTTPS
bash generate_cert.sh

# 4. Iniciar portal cautivo
sudo ./scripts/start_captive_portal.sh
```

**¡Listo!** El portal está corriendo. Conecta dispositivos a la red y se abrirá automáticamente.

---

## 📱 ¿Cómo Funciona?

### Para el Usuario

1. **Conectarse a la red WiFi**
2. **Notificación aparece automáticamente**: "Se requiere inicio de sesión"
3. **Click en notificación** → Abre navegador con portal
4. **Ingresar credenciales** (usuario: `student`, contraseña: `password`)
5. **¡Acceso concedido!** → Internet disponible

### Arquitectura Técnica

```
┌─────────────┐
│  Dispositivo│  
│   Cliente   │  
└──────┬──────┘
       │ 1. Intenta acceder a google.com
       ▼
┌─────────────┐
│ DNS Server  │  Responde: google.com → 192.168.1.1 (gateway)
│  (puerto 53)│
└──────┬──────┘
       │ 2. Navegador abre http://192.168.1.1
       ▼
┌─────────────┐
│  iptables   │  Redirige puertos 80/443 al portal
│  (firewall) │
└──────┬──────┘
       │ 3. Muestra página de login
       ▼
┌─────────────┐
│HTTP Server  │  Verifica credenciales
│  (puerto 80)│  Crea sesión + habilita internet
└─────────────┘
```

---

## 📁 Estructura del Proyecto

```
captive-portal/
├── server.py                    # Servidor HTTP/HTTPS con sockets
├── dns_server.py                # Servidor DNS falso
├── auth.py                      # Autenticación + hashing
├── users.json                   # Base de datos de usuarios
├── generate_cert.sh             # Generar certificados SSL
│
├── templates/
│   ├── index.html              # Página de login
│   └── success.html            # Página de éxito
│
├── scripts/
│   ├── start_captive_portal.sh # ⭐ Inicia todo el sistema
│   ├── stop_captive_portal.sh  # Detiene el portal
│   ├── enable_internet.sh      # Habilita acceso para una IP
│   ├── revoke_internet.sh      # Revoca acceso
│   ├── disable_internet.sh     # Bloquea internet + redirecciones
│   ├── nat_setup.sh            # Configura NAT
│   └── detect_interfaces.sh    # Detecta interfaces LAN/WAN
│
└── docs/                        # Documentación detallada
    ├── 01-DETECCION-AUTOMATICA.md
    ├── 02-HTTPS-SSL.md
    ├── 03-ANTI-SUPLANTACION.md
    ├── 04-NAT-MASQUERADING.md
    └── 05-DISENO-UX.md
```

---

## 👥 Gestión de Usuarios

### Agregar Usuario
```bash
python3 auth.py add estudiante mi_contraseña
```

### Actualizar Contraseña
```bash
python3 auth.py update estudiante nueva_contraseña
```

### Listar Usuarios
```bash
python3 auth.py list
```

---

## 🔒 Seguridad

- **Tokens de sesión**: `secrets.token_urlsafe(32)` - criptográficamente seguros
- **Hashing de contraseñas**: SHA-256 + salt + 1000 iteraciones
- **Anti-suplantación**: Verificación dual IP + MAC address
- **Cookies HttpOnly**: Previene acceso desde JavaScript
- **HTTPS opcional**: Encriptación TLS para credenciales

---

## 📚 Documentación

Cada requisito extra tiene su propia documentación detallada en `docs/`:

| Documento | Descripción |
|-----------|-------------|
| [01-DETECCION-AUTOMATICA.md](docs/01-DETECCION-AUTOMATICA.md) | DNS falso + notificaciones automáticas |
| [02-HTTPS-SSL.md](docs/02-HTTPS-SSL.md) | Configuración SSL/TLS |
| [03-ANTI-SUPLANTACION.md](docs/03-ANTI-SUPLANTACION.md) | Control de IP spoofing |
| [04-NAT-MASQUERADING.md](docs/04-NAT-MASQUERADING.md) | NAT/Masquerading |
| [05-DISENO-UX.md](docs/05-DISENO-UX.md) | Diseño web + UX |

---

## 🧪 Pruebas

### Verificar DNS
```bash
nslookup google.com 192.168.1.1
```

### Verificar HTTPS
```bash
curl -k https://192.168.1.1/
```

### Ver reglas iptables
```bash
sudo iptables -L -v -n
sudo iptables -t nat -L -v -n
```

### Logs en tiempo real
```bash
# Terminal 1: DNS logs
sudo tail -f /var/log/dns.log

# Terminal 2: Web server logs
sudo tail -f /var/log/portal.log
```

---

## 🛠️ Comandos Útiles

```bash
# Detener portal
sudo ./scripts/stop_captive_portal.sh

# Habilitar internet manualmente para una IP
sudo ./scripts/enable_internet.sh 192.168.1.50

# Revocar acceso
sudo ./scripts/revoke_internet.sh 192.168.1.50

# Limpiar reglas iptables
sudo iptables -F
sudo iptables -t nat -F
```

---

## 🎯 Cumplimiento de Requisitos

### ✅ Requisitos Mínimos

| Requisito | Cumplimiento | Evidencia |
|-----------|--------------|-----------|
| Endpoint HTTP de inicio de sesión | ✅ | `server.py` - Socket manual, parseo HTTP |
| Bloqueo de enrutamiento | ✅ | `disable_internet.sh` - iptables FORWARD DROP |
| Mecanismo de cuentas | ✅ | `auth.py` - CLI + JSON + hashing |
| Hilos/procesos para concurrencia | ✅ | `server.py` - threading.Thread por conexión |
| Solo biblioteca estándar | ✅ | Cero dependencias externas, solo stdlib |
| CLI del SO para firewall | ✅ | iptables + subprocess |

### ⭐ Requisitos Extras

| Requisito | Puntos | Evidencia |
|-----------|--------|-----------|
| Detección automática | 1.0 | `dns_server.py` + notificaciones OS |
| HTTPS válido | 0.5 | `ssl` module + OpenSSL |
| Anti-suplantación IP | 0.5 | Verificación IP+MAC con logs |
| NAT/Masquerading | 0.25 | iptables MASQUERADE |
| UX y diseño | 0.25 | Templates con gradientes + efectos |

---

## 💡 Tecnologías Usadas

**Backend:**
- Python 3 (stdlib): `socket`, `threading`, `ssl`, `hashlib`, `secrets`
- Bash: Scripts de configuración
- iptables: Firewall y NAT
- OpenSSL: Generación de certificados

**Frontend:**
- HTML5
- CSS3 (gradientes, efectos, responsive)
- SVG (iconos)

**Sin dependencias externas** - No requiere `pip install`

---

## 📖 Conceptos Implementados

- **Sockets TCP/IP**: Comunicación de red de bajo nivel
- **Protocolo HTTP**: Parseo manual de peticiones/respuestas
- **DNS Spoofing**: Servidor DNS falso para redirección
- **Firewall**: Reglas iptables (FORWARD, PREROUTING, POSTROUTING)
- **NAT/PAT**: Traducción de direcciones de red
- **SSL/TLS**: Encriptación de conexiones
- **Captive Portal Detection**: RFC 8910
- **Threading**: Concurrencia con locks
- **Hashing criptográfico**: SHA-256 con salt

---

## 🐛 Solución de Problemas

**No se detectan interfaces:**
- Ejecuta `ip addr` y configura manualmente en `detect_interfaces.sh`

**Clientes no son redirigidos:**
- Verifica DNS del cliente apunta al gateway
- Revisa reglas iptables: `sudo iptables -t nat -L -n`

**Sin internet después de login:**
- Verifica NAT: `sudo iptables -t nat -L -n | grep MASQUERADE`
- Verifica IP forwarding: `cat /proc/sys/net/ipv4/ip_forward` (debe ser 1)

**Permission denied:**
- Ejecuta scripts con `sudo`
- Verifica permisos: `chmod +x scripts/*.sh`

---

## 👨‍💻 Autor

**Tu Nombre**  
Proyecto de Redes - Universidad  
Diciembre 2025

---

## 📄 Licencia

MIT License - Proyecto académico

---

<p align="center">
  <b>⭐ Si te sirvió este proyecto, dale una estrella en GitHub ⭐</b>
</p>
