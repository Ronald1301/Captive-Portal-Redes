# HTTPS con SSL/TLS

**Requisito Extra:** 0.5 puntos  
**Estado:** ✅ Implementado

## 🔒 Descripción

El portal soporta conexiones HTTPS cifradas mediante SSL/TLS, protegiendo las credenciales durante la transmisión.

## 🚀 Uso Rápido

```bash
# 1. Generar certificados SSL
bash generate_cert.sh

# 2. Iniciar portal (detecta HTTPS automáticamente)
sudo ./scripts/start_captive_portal.sh

# 3. Acceder desde cliente
https://192.168.1.1/
```

## 🔧 Implementación

### Generación de Certificados

El script `generate_cert.sh` utiliza OpenSSL:

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout certs/server.key \
    -out certs/server.crt \
    -days 365 \
    -subj "/C=DO/ST=SD/L=SD/O=Universidad/OU=Redes/CN=portal.local"
```

### Servidor HTTPS

```python
# server.py
import ssl

class CaptivePortalServer:
    def __init__(self, use_ssl=False, certfile=None, keyfile=None):
        if use_ssl:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(certfile, keyfile)
    
    def start(self):
        client_socket, addr = self.server_socket.accept()
        
        if self.use_ssl:
            # Envolver socket con SSL
            client_socket = self.ssl_context.wrap_socket(
                client_socket, 
                server_side=True
            )
```

### Redirección Automática

El script `disable_internet.sh` detecta certificados y redirige:

```bash
if [ -f "certs/server.crt" ]; then
    # Redirigir HTTP y HTTPS al puerto 443
    iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 80 -j DNAT --to $LAN_IP:443
    iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 443 -j DNAT --to $LAN_IP:443
fi
```

## ⚠️ Certificados Autofirmados

Los navegadores mostrarán advertencia porque el certificado no está firmado por una CA confiable:

- **Chrome/Edge**: "Tu conexión no es privada"
- **Firefox**: "Advertencia: Riesgo potencial de seguridad"

**Solución:** Click en "Avanzado" → "Continuar de todos modos"

Para producción, usar certificados de Let's Encrypt o una CA comercial.

## 🧪 Verificación

### 1. Verificar puerto HTTPS
```bash
sudo netstat -tulpn | grep :443
# tcp  0  0.0.0.0:443  LISTEN  12345/python3
```

### 2. Probar conexión
```bash
curl -k https://192.168.1.1/
# -k ignora validación de certificado
```

### 3. Ver detalles del certificado
```bash
openssl s_client -connect 192.168.1.1:443 -showcerts
```

## 📂 Estructura

```
certs/
├── server.crt    # Certificado público
└── server.key    # Clave privada
```

## ✅ Verificación del Requisito

- ✅ HTTPS funcional con SSL/TLS
- ✅ Certificados autofirmados generados automáticamente
- ✅ Encriptación de credenciales en tránsito
- ✅ Detección automática de certificados al iniciar
- ✅ Usa módulo `ssl` de stdlib (sin dependencias externas)

## 🔐 Comandos Útiles

```bash
# Regenerar certificados
bash generate_cert.sh

# Iniciar solo HTTP
sudo python3 server.py --port 80

# Iniciar solo HTTPS
sudo python3 server.py --ssl --cert certs/server.crt --key certs/server.key

# Iniciar HTTPS en puerto personalizado
sudo python3 server.py --ssl --cert certs/server.crt --key certs/server.key --port 8443
```
