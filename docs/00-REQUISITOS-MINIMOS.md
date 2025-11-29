# Requisitos Mínimos del Portal Cautivo

**Puntuación:** 5.0 puntos  
**Estado:** ✅ Todos implementados

## 📋 Requisitos Obligatorios

### 1️⃣ Endpoint HTTP de Inicio de Sesión (sin bibliotecas externas)

**Implementación:** `server.py` - Servidor HTTP manual con sockets puros

#### ¿Qué significa?
- NO usar `http.server` de Python
- NO usar Flask, Django, FastAPI
- Implementar manualmente usando `socket` de la biblioteca estándar

#### Código Principal

```python
import socket
import threading

class CaptivePortalServer:
    def __init__(self, host='0.0.0.0', port=80):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
    
    def handle_client(self, client_socket, client_address):
        # Recibir petición HTTP raw
        request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
        
        # Parsear manualmente la petición
        lines = request_data.split('\r\n')
        request_line = lines[0]  # GET /login HTTP/1.1
        method, path, protocol = request_line.split()
        
        # Parsear headers
        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key] = value
        
        # Responder manualmente
        response = self.generate_response(method, path, headers)
        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()
    
    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address)
            )
            thread.start()
```

#### Verificación

```bash
# Ver que NO hay imports de bibliotecas externas
grep -E "^import|^from" server.py

# Output esperado (SOLO stdlib):
# import socket
# import threading
# import ssl
# import hashlib
# import json
# import subprocess
# import secrets
# import re
```

**✅ Cumple:** Solo usa `socket`, `threading`, `ssl` (todos de stdlib)

---

### 2️⃣ Bloqueo de Enrutamiento hasta Autenticación

**Implementación:** `scripts/disable_internet.sh` + `scripts/enable_internet.sh`

#### ¿Qué significa?
- Por defecto, NADIE tiene internet
- Solo después de autenticarse se habilita por IP individual
- Usar firewall (iptables) con política DROP

#### Configuración de Bloqueo

```bash
#!/bin/bash
# disable_internet.sh

# BLOQUEAR TODO EL FORWARDING (política por defecto: DROP)
iptables -P FORWARD DROP

# Permitir tráfico local (loopback)
iptables -A FORWARD -i lo -j ACCEPT
iptables -A FORWARD -o lo -j ACCEPT

# Permitir conexiones establecidas (para que el servidor funcione)
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# TODO LO DEMÁS: BLOQUEADO ❌
```

#### Habilitación por IP

```bash
#!/bin/bash
# enable_internet.sh <IP_CLIENTE>

IP=$1

# Permitir forwarding SOLO para esta IP específica
iptables -I FORWARD 1 -s $IP -j ACCEPT
iptables -I FORWARD 1 -d $IP -j ACCEPT

echo "✅ Internet habilitado para $IP"
```

#### Flujo de Autenticación

```
1. Cliente intenta acceder a google.com
   ↓
2. iptables: FORWARD DROP → ❌ Bloqueado
   ↓
3. Cliente se loguea en el portal
   ↓
4. server.py ejecuta: enable_internet.sh 192.168.1.50
   ↓
5. iptables crea regla: ACCEPT para 192.168.1.50
   ↓
6. ✅ Cliente tiene internet
```

#### Verificación

```bash
# Ver política de forwarding (debe ser DROP)
sudo iptables -L FORWARD -v -n

# Output esperado:
# Chain FORWARD (policy DROP 0 packets, 0 bytes)

# Ver IPs autorizadas
sudo iptables -L FORWARD -v -n | grep ACCEPT
```

**✅ Cumple:** iptables con política DROP + habilitación por IP

---

### 3️⃣ Mecanismo de Cuentas de Usuario

**Implementación:** `auth.py` + `users.json`

#### ¿Qué significa?
- Poder crear, actualizar, listar usuarios
- Almacenamiento persistente (JSON)
- Contraseñas hasheadas (no texto plano)
- Interfaz CLI para gestión

#### Estructura de `users.json`

```json
{
  "users": [
    {
      "username": "admin",
      "password": "sha256:1000:a1f3e8d9b2c4...:e9f2d8a7b3c5..."
    },
    {
      "username": "student",
      "password": "sha256:1000:x7y9z2k4m1...:p8q3r5s7t2..."
    }
  ]
}
```

**Formato del hash:**
```
algoritmo:iteraciones:salt:hash
sha256:1000:random_salt_hex:password_hash_hex
```

#### CLI de Gestión

```bash
# Agregar usuario
python3 auth.py add username password

# Actualizar contraseña
python3 auth.py update username nueva_password

# Listar usuarios
python3 auth.py list

# Verificar credenciales (interno)
python3 auth.py verify username password
```

#### Implementación del Hashing

```python
import hashlib
import secrets

def hash_password(password, salt=None, iterations=1000):
    """
    Genera hash seguro de contraseña con salt
    """
    if salt is None:
        salt = secrets.token_hex(16)  # 32 caracteres hex
    
    # Hashear con SHA-256 + salt + iteraciones
    pwd_hash = password.encode('utf-8')
    for _ in range(iterations):
        pwd_hash = hashlib.sha256(pwd_hash + salt.encode('utf-8')).hexdigest()
    
    return f"sha256:{iterations}:{salt}:{pwd_hash}"

def verify_password(password, password_hash):
    """
    Verifica si la contraseña coincide con el hash
    """
    parts = password_hash.split(':')
    if len(parts) != 4:
        return False
    
    algorithm, iterations, salt, stored_hash = parts
    
    # Re-generar hash con los mismos parámetros
    new_hash = hash_password(password, salt, int(iterations))
    
    # Comparación segura (timing-safe)
    return secrets.compare_digest(password_hash, new_hash)
```

#### Verificación

```bash
# Agregar usuario de prueba
python3 auth.py add test_user test_pass

# Verificar que el hash NO es texto plano
cat users.json | grep "test_user"

# Output esperado:
# "password": "sha256:1000:abc123....:def456..."
# NO debe aparecer "test_pass" en texto plano
```

**✅ Cumple:** CLI completo + JSON + hashing SHA-256 + salt + 1000 iteraciones

---

### 4️⃣ Concurrencia con Hilos o Procesos

**Implementación:** `threading.Thread` en `server.py`

#### ¿Qué significa?
- Soportar múltiples usuarios simultáneos
- Cada conexión en un thread/proceso separado
- No bloquear mientras un usuario se autentica

#### Implementación con Threading

```python
import threading

class CaptivePortalServer:
    def start(self):
        """
        Inicia el servidor y acepta conexiones
        """
        print(f"🚀 Servidor iniciado en {self.host}:{self.port}")
        
        while True:
            # Acepta nueva conexión (bloqueante)
            client_socket, client_address = self.server_socket.accept()
            
            print(f"📱 Nueva conexión desde {client_address[0]}:{client_address[1]}")
            
            # Crear thread para manejar esta conexión
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address),
                daemon=True  # Thread muere con el programa principal
            )
            
            # Iniciar thread (no bloqueante)
            client_thread.start()
            
            # El bucle continúa aceptando nuevas conexiones
            # mientras los threads anteriores siguen activos
```

#### Flujo de Concurrencia

```
Servidor escucha en puerto 80
    ↓
Cliente 1 se conecta → Thread 1 creado → Procesa petición
    ↓                                            ↓
Cliente 2 se conecta → Thread 2 creado → Procesa petición
    ↓                                            ↓
Cliente 3 se conecta → Thread 3 creado → Procesa petición
    ↓
Servidor sigue aceptando conexiones...

Todos los threads corren en paralelo ✅
```

#### Protección de Datos Compartidos

```python
import threading

class CaptivePortalServer:
    def __init__(self):
        # Lock para proteger diccionarios compartidos
        self.sessions_lock = threading.Lock()
        self.sessions = {}  # Sesiones activas
        
        self.authorized_ips_lock = threading.Lock()
        self.authorized_ips = set()  # IPs autorizadas
    
    def add_session(self, ip, token):
        """
        Agrega sesión de forma thread-safe
        """
        with self.sessions_lock:
            self.sessions[ip] = {
                'token': token,
                'created': time.time()
            }
    
    def is_authorized(self, ip):
        """
        Verifica autorización de forma thread-safe
        """
        with self.authorized_ips_lock:
            return ip in self.authorized_ips
```

#### Verificación

```bash
# Iniciar servidor
sudo python3 server.py &

# Simular múltiples conexiones simultáneas
for i in {1..10}; do
  curl http://localhost/ &
done

# Ver threads activos
ps -T -p $(pgrep -f "python3 server.py")

# Output esperado: múltiples threads (TID diferentes)
```

**✅ Cumple:** `threading.Thread` por conexión + locks para datos compartidos

---

## 🎯 Resumen de Cumplimiento

| Requisito | Evidencia | Archivo |
|-----------|-----------|---------|
| ✅ Servidor HTTP manual | Sockets puros, sin librerías web | `server.py` líneas 47-418 |
| ✅ Bloqueo de internet | iptables FORWARD DROP | `scripts/disable_internet.sh` |
| ✅ Cuentas de usuario | CLI + JSON + hashing | `auth.py` + `users.json` |
| ✅ Concurrencia | threading.Thread | `server.py` líneas 418-421 |

---

## 🧪 Pruebas de Validación

### Test 1: Verificar imports (solo stdlib)

```bash
grep -E "^import|^from" *.py | grep -v "socket\|threading\|ssl\|hashlib\|json\|subprocess\|secrets\|re\|argparse\|time"
```

**Resultado esperado:** Sin output (no hay imports externos)

### Test 2: Verificar bloqueo por defecto

```bash
sudo iptables -L FORWARD -v -n | head -1
```

**Resultado esperado:** `Chain FORWARD (policy DROP ...)`

### Test 3: Verificar hashing de contraseñas

```bash
python3 auth.py add test test123
cat users.json | grep "test123"
```

**Resultado esperado:** Sin output (contraseña hasheada, no texto plano)

### Test 4: Verificar concurrencia

```bash
# Terminal 1: Iniciar servidor
sudo python3 server.py

# Terminal 2: 10 conexiones simultáneas
ab -n 10 -c 10 http://localhost/
```

**Resultado esperado:** Las 10 peticiones se completan correctamente

---

## 📚 Referencias de Código

- **Servidor HTTP manual:** `server.py` líneas 47-298
- **Parseo de peticiones:** `server.py` líneas 63-94
- **Threading:** `server.py` líneas 418-421
- **Hashing de contraseñas:** `auth.py` líneas 9-50
- **CLI de usuarios:** `auth.py` líneas 100-160
- **Bloqueo iptables:** `scripts/disable_internet.sh` líneas 20-45
- **Habilitación por IP:** `scripts/enable_internet.sh` líneas 15-30

---

**Conclusión:** Los 4 requisitos mínimos están completamente implementados usando únicamente la biblioteca estándar de Python y herramientas nativas de Linux (iptables, bash). El proyecto cumple al 100% con las especificaciones base (5.0 puntos).
