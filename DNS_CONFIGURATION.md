# Configuración del Portal Cautivo - DNS y Redireccionamiento

## Requisitos del Sistema

- Linux (probado en Ubuntu/Debian)
- Python 3.7+
- Permisos de root (sudo)
- Conocimiento básico de redes y Linux

## Componentes

### 1. Servidor HTTP (server.py)
- Puerto: 80
- Maneja login, registro y logout
- Carga templates HTML desde `/templates`

### 2. Servidor DNS Falso (dns_server.py)
- Puerto: 53 (requiere root)
- Redirige **todas** las consultas DNS a la IP del gateway
- Detecta automáticamente intentos de conexión de clientes

### 3. Firewall Manager (firewall.py)
- Usa iptables para controlar acceso
- Bloquea/permite IPs específicas
- Limpia conexiones establecidas en logout

### 4. Session Manager (sessions.py)
- Gestiona sesiones activas
- Verifica login duplicados
- Limpia sesiones expiradas

### 5. User Manager (users.py)
- Almacena usuarios en JSON
- Hash SHA-256 de contraseñas
- Validación de login/registro

## Configuración Paso a Paso

### Paso 1: Configurar la Interfaz de Red

La interfaz de red debe estar configurada para actuar como gateway. Ejemplo:

```bash
# Ver interfaces disponibles
ip link show

# Configurar interfaz (ejemplo con eth0)
sudo ip addr add 192.168.137.1/24 dev eth0
sudo ip link set eth0 up

# Habilitar forwarding de IP
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

**Nota:** Reemplaza `eth0` con tu interfaz real y `192.168.137.1` con tu IP de gateway

### Paso 2: Ejecutar el Portal

```bash
# Desde la raíz del proyecto
sudo python3 main.py --gateway-ip 192.168.137.1
```

O si quieres que auto-detecte la IP:

```bash
sudo python3 main.py
```

### Paso 3: Configurar Clientes

Los clientes (teléfonos, laptops) deben:

1. Conectarse a la red WiFi/Ethernet del gateway
2. Configurar el gateway como:
   - **Gateway**: 192.168.137.1
   - **DNS**: 192.168.137.1 (el servidor DNS falso)

En la mayoría de redes WiFi, esto se configura automáticamente.

## Cómo Funciona el Redireccionamiento

### Flujo de Detección Automática

```
1. Cliente se conecta a la red
   ↓
2. Cliente intenta acceder a cualquier sitio web
   ↓
3. Cliente genera consulta DNS (ej: google.com)
   ↓
4. Servidor DNS (puerto 53) intercepta la consulta
   ↓
5. DNS responde: "google.com → 192.168.137.1"
   ↓
6. Cliente intenta conectar a 192.168.137.1:80
   ↓
7. Servidor HTTP (puerto 80) responde con el portal cautivo
   ↓
8. Cliente ve la página de login
```

### Reglas de Iptables

El firewall implementa estas reglas:

```bash
# Permitir conexiones establecidas y relacionadas
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Para cada usuario autenticado
iptables -A FORWARD -s <IP_CLIENTE> -j ACCEPT

# Bloquear por defecto
iptables -P FORWARD DROP

# NAT para internet saliente
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

## Archivos Importantes

### Templates HTML (`/templates/`)
- `index.html` - Página de login
- `register.html` - Página de registro
- `success.html` - Página de éxito

### Base de Datos (`users.json`)
```json
{
  "admin": "hash_de_contraseña",
  "usuario1": "hash_de_contraseña"
}
```

### Logs
El sistema genera logs en consola con formato:
```
YYYY-MM-DD HH:MM:SS - NOMBRE_MODULO - NIVEL - Mensaje
```

## Solución de Problemas

### Error: "Port 53 already in use"
```bash
# Ver qué proceso usa puerto 53
sudo lsof -i :53

# Matar el proceso
sudo kill -9 <PID>
```

### Error: "Permission denied" en puerto 80
```bash
# Ejecutar con sudo
sudo python3 main.py --gateway-ip 192.168.137.1
```

### Clientes no ven el portal
1. Verificar que DNS está respondiendo:
   ```bash
   nslookup google.com <IP_GATEWAY>
   ```

2. Verificar que HTTP responde:
   ```bash
   curl http://<IP_GATEWAY>/
   ```

3. Verificar reglas de firewall:
   ```bash
   sudo iptables -L FORWARD -v
   ```

### Usuario no puede acceder a internet después de login
1. Verificar que iptables tiene la regla ACCEPT:
   ```bash
   sudo iptables -L FORWARD -v | grep <IP_CLIENTE>
   ```

2. Verificar NAT:
   ```bash
   sudo iptables -t nat -L POSTROUTING -v
   ```

## Estadísticas y Monitoreo

Para ver el estado del portal:

```python
portal.status()
```

Mostrará:
- Sesiones activas
- Usuarios registrados
- IPs con acceso permitido

## Comandos Útiles

```bash
# Ver sesiones activas en tiempo real
sudo iptables -L FORWARD -v -n

# Ver estadísticas de iptables
sudo iptables -L -v -n -x

# Limpiar todas las reglas de firewall
sudo iptables -F
sudo iptables -t nat -F

# Verificar si el DNS está escuchando
sudo netstat -ulpn | grep :53

# Ver logs en tiempo real
sudo tail -f /var/log/syslog
```

## Configuración Avanzada

### Cambiar puerto HTTP
Edita `main.py`:
```python
PORT = 8080  # En lugar de 80
```

### Cambiar timeout de sesión
Edita `main.py`:
```python
SESSION_TIMEOUT = 7200  # 2 horas en lugar de 1 hora
```

### Cambiar interfaz de red
Edita `main.py`:
```python
INTERFACE = "wlan0"  # En lugar de eth0
```

## Notas de Seguridad

- ⚠️ El portal NO usa HTTPS por defecto (inseguro)
- ⚠️ Las contraseñas se almacenan en JSON (considera usar una BD real)
- ⚠️ Requiere permisos de root para ejecutarse
- ✅ Las contraseñas se hashean con SHA-256
- ✅ Las sesiones expiran automáticamente
- ✅ Se verifica login duplicado desde múltiples IPs

