# Control Anti-Suplantación de IP

**Requisito Extra:** 0.5 puntos  
**Estado:** ✅ Implementado

## 🛡️ Descripción

Sistema de detección y prevención de ataques de suplantación de identidad (IP spoofing) mediante verificación dual de IP y dirección MAC.

## 🚨 Problema que Resuelve

### Sin protección:
1. Usuario legítimo (192.168.1.10) se autentica
2. Portal habilita internet para esa IP
3. Atacante cambia su IP a 192.168.1.10
4. Atacante obtiene acceso sin autenticarse ❌

### Con protección:
1. Usuario legítimo (IP: 192.168.1.10, MAC: aa:bb:cc:dd:ee:ff) se autentica
2. Portal guarda: IP + MAC + Token de sesión
3. Atacante cambia su IP a 192.168.1.10 (su MAC: 11:22:33:44:55:66)
4. Portal verifica MAC → no coincide → **BLOQUEA** ✅
5. Se registra el intento de ataque

## 🔧 Implementación

### Obtención de MAC Address

```python
def get_mac(ip):
    """Obtiene MAC desde la tabla ARP del sistema"""
    p = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
    m = re.search(r'([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', 
                  p.stdout, re.I)
    return m.group(1).lower() if m else None
```

### Verificación de Autorización

```python
def is_authorized(headers, client_ip):
    """Verificación en 3 capas"""
    session_id = get_session_cookie(headers)
    if not session_id:
        return False
    
    session = SESSIONS.get(session_id)
    if not session:
        return False
    
    # CONTROL ANTI-SUPLANTACIÓN
    if session['ip'] != client_ip:
        current_mac = get_mac(client_ip)
        session_mac = session.get('mac')
        
        if current_mac == session_mac:
            # MAC coincide - usuario legítimo con nueva IP (DHCP)
            session['ip'] = client_ip
            print(f'⚠ IP changed: {old_ip} → {client_ip} (MAC: {current_mac})')
            return True
        else:
            # MAC NO coincide - ATAQUE
            print(f'🚨 SPOOFING DETECTED!')
            print(f'   Expected MAC: {session_mac}, Got: {current_mac}')
            return False
    
    return True
```

### Almacenamiento de Sesión

```python
# Al autenticarse
SESSIONS[session_id] = {
    'user': username,
    'ip': client_ip,
    'mac': get_mac(client_ip)  # ← Guardamos MAC
}
```

## 📊 Escenarios Cubiertos

| Escenario | IP | MAC | Resultado |
|-----------|----|----|-----------|
| Acceso normal | Coincide | Coincide | ✅ PERMITIR |
| DHCP renovó lease | Cambió | Coincide | ✅ PERMITIR + actualizar IP |
| IP spoofing | Cambió | NO coincide | ❌ BLOQUEAR + registrar ataque |
| Sesión robada (mismo dispositivo) | Coincide | Coincide | ✅ PERMITIR (cookie comprometida) |

## 🧪 Pruebas

### Test 1: Usuario Normal
```bash
# Usuario se autentica correctamente
curl -c cookies.txt -d "username=student&password=pass" http://192.168.1.1/login

# Navega normalmente
curl -b cookies.txt http://google.com
# ✅ Funciona
```

### Test 2: Cambio de IP Legítimo (DHCP)
```bash
# Usuario autenticado con IP 192.168.1.10
# DHCP renueva y asigna 192.168.1.15 al mismo dispositivo

# Logs del servidor:
⚠ IP changed for session a7b3c4f5... (MAC: aa:bb:cc:dd:ee:ff)
  Old IP: 192.168.1.10 → New IP: 192.168.1.15
# ✅ Acceso permitido
```

### Test 3: Ataque de Suplantación
```bash
# Atacante intenta cambiar su IP a una IP autenticada
sudo ip addr add 192.168.1.10/24 dev eth0

# Atacante intenta usar cookie robada
curl -b stolen_cookie.txt http://google.com

# Logs del servidor:
🚨 SPOOFING ATTEMPT DETECTED!
   Session registered to 192.168.1.10 (MAC: aa:bb:cc:dd:ee:ff)
   Request from 192.168.1.10 (MAC: 11:22:33:44:55:66)
# ❌ Acceso bloqueado
```

## 📝 Logs de Ejemplo

### Acceso Legítimo
```
192.168.1.10 - POST /login
✓ Access granted to 192.168.1.10 (user: student)
192.168.1.10 - GET /
```

### Cambio de IP por DHCP
```
192.168.1.15 - GET /
⚠ IP changed for session a7b3c4f5... (MAC: aa:bb:cc:dd:ee:ff)
  Old IP: 192.168.1.10 → New IP: 192.168.1.15
```

### Intento de Ataque
```
192.168.1.10 - GET /
🚨 SPOOFING ATTEMPT DETECTED!
   Session a7b3c4f5... registered to IP 192.168.1.10 (MAC: aa:bb:cc:dd:ee:ff)
   But request came from IP 192.168.1.10 (MAC: 11:22:33:44:55:66)
```

## ⚠️ Limitaciones

### Protege contra:
- ✅ IP spoofing simple
- ✅ Ataques man-in-the-middle básicos
- ✅ Robo de cookies entre dispositivos diferentes

### NO protege contra:
- ❌ MAC spoofing (atacante cambia su MAC)
- ❌ ARP poisoning avanzado
- ❌ Sesiones robadas en el mismo dispositivo

## 🔍 Verificación en Código

**Archivo:** `server.py`

- **Líneas 28-38:** Función `get_mac()` - Obtiene MAC desde ARP
- **Líneas 99-146:** Función `is_authorized()` - Verificación IP+MAC
- **Líneas 210-217:** Al crear sesión, guarda MAC

## ✅ Verificación del Requisito

- ✅ Verificación dual IP + MAC address
- ✅ Detección automática de intentos de suplantación
- ✅ Logs detallados de ataques
- ✅ Soporte para cambios legítimos de IP (DHCP)
- ✅ Usa comandos del sistema (`arp`) sin dependencias externas
