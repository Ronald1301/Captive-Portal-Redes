# Detección Automática del Portal Cautivo

**Requisito Extra:** 1.0 punto  
**Estado:** ✅ Implementado

## 📱 Descripción

Cuando un dispositivo se conecta a la red, automáticamente detecta que debe autenticarse y muestra una notificación con un hipervínculo directo a la página de login.

## 🔧 Cómo Funciona

### Flujo Completo

```
1. Dispositivo se conecta a la red
   ↓
2. Sistema operativo verifica conectividad a internet
   - Android: connectivitycheck.gstatic.com
   - iOS: captive.apple.com
   - Windows: www.msftconnecttest.com
   ↓
3. DNS Server falso responde: todas las URLs → IP del gateway
   ↓
4. Sistema detecta: "Esto es un portal cautivo"
   ↓
5. Muestra notificación automática con botón/hipervínculo
   ↓
6. Usuario hace clic → Abre navegador con la página de login
```

### Notificaciones por Sistema Operativo

**Android:**
- Notificación: "Se requiere inicio de sesión en la red Wi-Fi"
- Botón: "Tocar para iniciar sesión"

**iOS/macOS:**
- Ventana emergente automática con el portal
- Se abre Safari en modo "Captive Portal"

**Windows:**
- Notificación: "Se requiere una acción para conectarse"
- Botón: "Abrir"

**Linux (GNOME/KDE):**
- Banner de notificación
- Click abre navegador automáticamente

## 💻 Implementación

### Archivo: `dns_server.py`

```python
class DNSQuery:
    def response(self, ip):
        """Genera respuesta DNS apuntando al gateway"""
        # Responde TODAS las consultas con la IP del gateway
        packet = build_dns_response(self.data, ip)
        return packet

class DNSServer:
    def handle_request(self, data, addr):
        query = DNSQuery(data)
        # Redirige TODO al gateway
        response = query.response(self.redirect_ip)
        self.sock.sendto(response, addr)
```

### URLs Interceptadas

El servidor DNS responde a todas las consultas, incluyendo:

- `connectivitycheck.gstatic.com` (Android)
- `captive.apple.com` (iOS/macOS)
- `www.msftconnecttest.com` (Windows)
- `connectivity-check.ubuntu.com` (Ubuntu)
- `google.com`, `facebook.com`, cualquier dominio

## 🧪 Pruebas

### Verificar DNS

```bash
# Desde un cliente en la red
nslookup google.com 192.168.1.1

# Respuesta esperada:
# Server:  192.168.1.1
# Address: 192.168.1.1
# 
# Name:    google.com
# Address: 192.168.1.1  ← IP del gateway
```

### Logs del Servidor

```bash
sudo ./scripts/start_captive_portal.sh

# Verás:
DNS Query from 192.168.1.50: connectivitycheck.gstatic.com -> 192.168.1.1
DNS Query from 192.168.1.50: www.google.com -> 192.168.1.1
192.168.1.50 - GET /
```

## ✅ Verificación del Requisito

- ✅ Detección automática sin configuración manual
- ✅ Funciona en Android, iOS, Windows, macOS, Linux
- ✅ Notificación aparece automáticamente
- ✅ Hipervínculo directo a la página de login
- ✅ Usa protocolo estándar (RFC 8910 - Captive Portal Detection)

## 📚 Referencias

- [RFC 8910 - Captive-Portal Identification](https://datatracker.ietf.org/doc/html/rfc8910)
- [Android Captive Portal Detection](https://android.googlesource.com/platform/frameworks/base/+/master/services/core/java/com/android/server/connectivity/NetworkMonitor.java)
