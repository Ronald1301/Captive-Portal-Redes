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
# Portal Cautivo - Proyecto Redes 2025

Sistema de portal cautivo que controla el acceso a la red hasta que los usuarios se autentiquen. Implementado en Python puro (solo stdlib) y usando iptables vía CLI para el firewall.

---

## ✨ Características principales

- **Servidor HTTP propio** (sin http.server, solo sockets) para el portal de login ([server.py](server.py))
- **Gestión de usuarios** con almacenamiento seguro en JSON y hashing SHA-256 ([users.py](users.py), [users.json](users.json))
- **Gestión de sesiones** con expiración automática y control de concurrencia ([sessions.py](sessions.py))
- **Firewall dinámico** usando iptables para bloquear/permitir acceso según autenticación ([firewall.py](firewall.py))
- **Portal web moderno**: login con diseño responsive y mensajes de error/exito
- **Sin dependencias externas**: solo Python estándar y comandos del sistema

---

## 🚀 Inicio rápido

### Requisitos
- Linux (Ubuntu/Debian/CentOS)
- Python 3.6+
- iptables instalado
- Privilegios de root (sudo)

### Ejecución

```bash
sudo python3 main.py
```

El portal quedará escuchando en la IP y puerto configurados (por defecto 192.168.137.1:80).

---

## 📁 Estructura del proyecto

```
Captive-Portal-Redes/
├── main.py           # Arranque y ciclo de vida del portal cautivo
├── server.py         # Servidor HTTP y lógica de login
├── firewall.py       # Gestión de reglas iptables
├── sessions.py       # Gestión de sesiones y expiración
├── users.py          # Gestión de usuarios y autenticación
├── users.json        # Base de datos de usuarios (hashes)
├── captiveportal.md  # Enunciado y requisitos del proyecto
├── README.md         # Este archivo
```

---

## 👥 Gestión de usuarios

Los usuarios se definen en [users.json](users.json) y se gestionan desde el propio portal (no hay CLI externa):

- **Agregar usuario**: Solo modificando el archivo o extendiendo [users.py](users.py)
- **Eliminar usuario**: Idem
- **Listar usuarios**: Desde el código o inspeccionando el JSON

---

## 🔒 Seguridad

- Contraseñas almacenadas como SHA-256 (sin salt)
- Acceso a la red solo tras autenticación exitosa
- Expiración automática de sesiones
- Firewall bloquea todo tráfico hasta login
- Sin dependencias externas

---

## 🧪 Pruebas y comandos útiles

Ver reglas iptables:
```bash
sudo iptables -L -v -n
sudo iptables -t nat -L -v -n
```

Limpiar reglas iptables:
```bash
sudo iptables -F
sudo iptables -t nat -F
```

---

## 🎯 Cumplimiento de requisitos

Tabla de cumplimiento según [captiveportal.md](captiveportal.md):

| Requisito                                         | ¿Cumplido? | Evidencia (archivo)         |
|---------------------------------------------------|:----------:|-----------------------------|
| Endpoint http de inicio de sesión en la red        |     ✅     | [server.py](server.py)      |
| Bloqueo de enrutamiento hasta login                |     ✅     | [firewall.py](firewall.py)  |
| Mecanismo de definición de cuentas de usuario      |     ✅     | [users.py](users.py), [users.json](users.json) |
| Manejo de varios usuarios concurrentes (hilos)     |     ✅     | [server.py](server.py), [sessions.py](sessions.py) |
| Solo biblioteca estándar y CLI del SO              |     ✅     | Todo el código, README      |

### Extras (no implementados en este repo base)

| Extra                                              | ¿Implementado? | Comentario |
|----------------------------------------------------|:-------------:|------------|
| Detección automática del portal cautivo            |       ❌       |            |
| HTTPS válido sobre la URL del portal               |       ❌       |            |
| Control de suplantación de IPs                     |       ❌       |            |
| Servicio de enmascaramiento IP (NAT/Masquerading)  |       ✅       | [firewall.py](firewall.py) |
| Experiencia de usuario y diseño web moderno        |       ✅       | [server.py](server.py) (HTML login) |
| Creatividad                                        |       —        |            |

---

## ℹ️ Notas

- El sistema está pensado para pruebas en laboratorio/entorno controlado.
- Para producción, se recomienda agregar salt a los hashes, soporte HTTPS y controles anti-suplantación.
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
