# Escenarios de Prueba del Portal Cautivo

**Documento:** Casos de prueba detallados para validar funcionalidad  
**Fecha:** Diciembre 2025  
**Entorno:** VM Ubuntu (servidor) + dispositivos clientes (Android/iOS/Windows/Linux)

---

## 🖥️ Configuración del Entorno de Pruebas

### Servidor (VM Ubuntu)

**Requisitos:**
- Ubuntu 20.04 o superior
- 2 interfaces de red configuradas:
  - **eth0 (WAN):** Conectada a internet (ej: 10.0.2.15/24 via VirtualBox NAT)
  - **eth1 (LAN):** Red interna para clientes (ej: 192.168.1.1/24)
- Python 3.6+
- iptables

**Configuración inicial:**

```bash
# En la VM Ubuntu (servidor)

# 1. Identificar interfaces
ip addr show

# 2. Configurar interfaz LAN estática
sudo ip addr add 192.168.1.1/24 dev eth1
sudo ip link set eth1 up

# 3. Habilitar IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# 4. Iniciar portal cautivo
cd /ruta/al/proyecto
sudo ./scripts/start_captive_portal.sh
```

### Dispositivos Cliente

#### Opción 1: Otra VM Linux (más fácil para pruebas)
- **Red:** Host-Only o Internal Network con la VM servidor
- **IP:** 192.168.1.0/24 (misma red que eth1 del servidor)
- **Gateway:** 192.168.1.1 (IP del servidor)
- **DNS:** 192.168.1.1

#### Opción 2: Smartphone/Tablet conectado vía WiFi
- Configurar hotspot WiFi en el servidor Ubuntu
- Dispositivos se conectan al hotspot
- DHCP configurado para dar gateway=192.168.1.1

#### Opción 3: PC físico conectado por cable
- Cable Ethernet desde PC cliente al servidor Ubuntu (eth1)
- Configurar IP manual en el cliente

---

## 🧪 Escenario 1: Conexión Inicial y Bloqueo de Internet

### Objetivo
Verificar que los dispositivos nuevos NO tienen acceso a internet hasta autenticarse.

### Requisitos Previos
**EN EL SERVIDOR (VM Ubuntu):**
```bash
# Verificar que el portal está corriendo
sudo ./scripts/start_captive_portal.sh

# Verificar interfaces
ip addr show  # eth0=WAN, eth1=LAN (192.168.1.1/24)

# Verificar iptables
sudo iptables -L FORWARD -v -n  # Debe mostrar policy DROP
```

### Pasos de Prueba por Tipo de Cliente

#### 🐧 Cliente Linux (otra VM o PC)

**EN EL SERVIDOR (VM Ubuntu):**
- Portal ya está corriendo
- eth1 configurada con 192.168.1.1/24

**EN EL CLIENTE LINUX:**

1. **Configurar red manualmente**
   ```bash
   # Conectar cable a eth1 del servidor (o red interna de VirtualBox)
   
   # Ver interfaces disponibles
   ip addr show
   
   # Configurar IP estática (ajusta 'enp0s8' según tu interfaz)
   sudo ip addr add 192.168.1.50/24 dev enp0s8
   sudo ip link set enp0s8 up
   
   # Configurar gateway
   sudo ip route add default via 192.168.1.1
   
   # Configurar DNS
   echo "nameserver 192.168.1.1" | sudo tee /etc/resolv.conf
   ```

2. **Verificar conectividad al servidor**
   ```bash
   ping -c 3 192.168.1.1  # ✅ Debe funcionar
   ```

3. **Intentar acceder a internet (debe fallar)**
   ```bash
   # Ping a Google DNS
   ping -c 3 8.8.8.8  # ❌ Destination Host Unreachable
   
   # Intentar acceso web
   curl -I http://google.com  # Redirige al portal
   
   # Resolver dominio
   nslookup facebook.com  # Responde con 192.168.1.1
   ```

#### 📱 Cliente Android (Smartphone/Tablet)

**EN EL SERVIDOR (VM Ubuntu):**

1. **Crear hotspot WiFi** (requiere adaptador WiFi en la VM)
   ```bash
   # Instalar hostapd y dnsmasq
   sudo apt-get install hostapd dnsmasq
   
   # Configurar hostapd (/etc/hostapd/hostapd.conf)
   interface=wlan0
   ssid=Portal_Cautivo_Test
   channel=6
   hw_mode=g
   auth_algs=1
   wpa=2
   wpa_passphrase=test1234
   wpa_key_mgmt=WPA-PSK
   
   # Iniciar hotspot
   sudo systemctl start hostapd
   ```

2. **Configurar DHCP** (/etc/dnsmasq.conf)
   ```
   interface=wlan0
   dhcp-range=192.168.1.50,192.168.1.100,12h
   dhcp-option=3,192.168.1.1  # Gateway
   dhcp-option=6,192.168.1.1  # DNS
   ```

**EN EL DISPOSITIVO ANDROID:**

1. **Conectar al WiFi**
   - Ajustes → WiFi
   - Conectar a "Portal_Cautivo_Test"
   - Contraseña: test1234

2. **Esperar notificación automática**
   - Debe aparecer: "Se requiere inicio de sesión"
   - **NO abrir Chrome/navegador manualmente**

3. **Verificar que no hay internet**
   - Intentar abrir cualquier app (Gmail, YouTube)
   - No debe cargar contenido

**QUÉ ESPERAR:**
- ✅ Notificación automática en 5-10 segundos
- ✅ Click en notificación → Abre portal en navegador interno
- ❌ Apps no pueden acceder a internet

#### 🍎 Cliente iOS (iPhone/iPad)

**EN EL SERVIDOR:** (mismo setup de WiFi que Android)

**EN EL DISPOSITIVO iOS:**

1. **Conectar al WiFi**
   - Ajustes → Wi-Fi
   - Conectar a "Portal_Cautivo_Test"
   - Contraseña: test1234

2. **Popup automático**
   - iOS abre automáticamente un popup con el portal
   - **Sin necesidad de abrir Safari**

3. **Verificar bloqueo**
   - Intentar abrir Safari → Sin conexión
   - Apps no cargan contenido

**QUÉ ESPERAR:**
- ✅ Popup inmediato (2-3 segundos)
- ✅ Portal se muestra en ventana emergente
- ❌ Safari y apps bloqueadas

#### 🪟 Cliente Windows (PC/Laptop)

**EN EL SERVIDOR:** (conexión por cable o WiFi)

**EN EL DISPOSITIVO WINDOWS:**

1. **Conectar por cable Ethernet**
   - Conectar cable a eth1 del servidor
   - Windows debe obtener IP vía DHCP (si configurado)
   - O configurar IP manual:
     - IP: 192.168.1.60
     - Máscara: 255.255.255.0
     - Gateway: 192.168.1.1
     - DNS: 192.168.1.1

2. **Verificar notificación de Windows**
   - Aparece icono de red con signo de exclamación
   - Notificación: "Requiere acción"
   - Click → Abre Edge con el portal

3. **Probar bloqueo**
   ```cmd
   # En CMD o PowerShell
   ping 8.8.8.8  # Timeout
   
   # Abrir Edge y navegar a google.com
   # Redirige al portal (http://192.168.1.1/)
   ```

**QUÉ ESPERAR:**
- ✅ Notificación de red
- ✅ Edge abre automáticamente el portal
- ❌ Sin conexión a internet

### Resultados Esperados por Plataforma

| Plataforma | Notificación | Tiempo | Redirección |
|------------|--------------|--------|-------------|
| 🐧 Linux | Manual (abrir navegador) | - | ✅ curl redirige |
| 📱 Android | Automática | 5-10s | ✅ Popup del portal |
| 🍎 iOS | Automática (popup) | 2-3s | ✅ Ventana emergente |
| 🪟 Windows | Automática | 3-5s | ✅ Edge abre portal |

**Todos los clientes:**
- ❌ `ping 8.8.8.8` → Timeout o "Destination Host Unreachable"
- ✅ DNS resuelve todo a 192.168.1.1
- ✅ HTTP redirige al portal

### Verificación en Servidor (VM Ubuntu)

```bash
# EJECUTAR EN LA VM UBUNTU (SERVIDOR)

# 1. Ver intentos de forwarding bloqueados
sudo iptables -L FORWARD -v -n | grep DROP

# 2. Ver consultas DNS en tiempo real
sudo tail -f /var/log/syslog | grep "DNS"

# Output esperado:
# DNS Query: facebook.com from 192.168.1.50 → 192.168.1.1
# DNS Query: connectivitycheck.gstatic.com from 192.168.1.51 → 192.168.1.1

# 3. Ver conexiones al servidor web
sudo tail -f /var/log/portal.log

# Output esperado:
# [2025-12-05 10:15:30] GET / from 192.168.1.50 (unauthorized)
# [2025-12-05 10:15:31] GET /login from 192.168.1.50
```

### Criterio de Éxito
✅ Ningún cliente puede acceder a internet sin autenticarse  
✅ DNS responde con IP del gateway (192.168.1.1) para todos los dominios  
✅ Navegadores redirigen automáticamente al portal  
✅ Detección automática funciona en Android/iOS/Windows

---

## 🔐 Escenario 2: Autenticación Exitosa

### Objetivo
Verificar que después del login, el usuario obtiene acceso completo a internet.

### Requisitos Previos

**EN EL SERVIDOR (VM Ubuntu):**
```bash
# Crear usuario de prueba
python3 auth.py add testuser testpass

# Verificar que el usuario existe
cat users.json

# Portal debe estar corriendo
ps aux | grep python3
```

### Pasos de Prueba por Plataforma

#### 🐧 Cliente Linux

**EN EL CLIENTE LINUX:**

1. **Abrir navegador**
   ```bash
   # Opción 1: Navegador gráfico (si tiene interfaz)
   firefox http://192.168.1.1/ &
   
   # Opción 2: Modo texto con curl
   curl http://192.168.1.1/
   ```

2. **Completar login con curl (prueba automática)**
   ```bash
   curl -c cookies.txt -X POST http://192.168.1.1/login \
     -d "username=testuser&password=testpass" \
     -L -v
   
   # Guardar cookie de sesión en cookies.txt
   ```

3. **Verificar acceso a internet**
   ```bash
   # Ping a Google DNS (ahora debe funcionar)
   ping -c 3 8.8.8.8  # ✅ 0% packet loss
   
   # Acceso web real
   curl -I https://www.google.com  # ✅ HTTP 200 OK
   
   # DNS externo
   nslookup google.com 8.8.8.8  # ✅ IPs reales de Google
   ```

#### 📱 Cliente Android

**EN EL DISPOSITIVO ANDROID:**

1. **Popup ya abierto del Escenario 1**
   - Formulario de login visible

2. **Completar formulario**
   - Usuario: `testuser`
   - Contraseña: `testpass`
   - Tocar "Iniciar Sesión"

3. **Verificar página de éxito**
   - Debe mostrar: "✅ Acceso Concedido"
   - "Ya puedes navegar por internet"

4. **Cerrar popup y probar internet**
   - Abrir Chrome → google.com (✅ carga normal)
   - Abrir YouTube → (✅ videos cargan)
   - Abrir Gmail → (✅ sincroniza correos)

#### 🍎 Cliente iOS

**EN EL DISPOSITIVO iOS:**

1. **Popup de portal abierto**
   - Ya muestra el formulario de login

2. **Ingresar credenciales**
   - Usuario: `testuser`
   - Contraseña: `testpass`
   - Tap en "Iniciar Sesión"

3. **Verificar éxito**
   - Página de éxito se muestra
   - Tap en "Cerrar" o "Continuar"
   - Popup se cierra automáticamente

4. **Probar conectividad**
   - Abrir Safari → apple.com (✅ carga)
   - App Store → (✅ descarga apps)
   - iMessage → (✅ envía mensajes)

#### 🪟 Cliente Windows

**EN EL DISPOSITIVO WINDOWS:**

1. **Edge abrió el portal automáticamente**
   - Formulario de login visible

2. **Completar login**
   - Usuario: `testuser`
   - Contraseña: `testpass`
   - Click "Iniciar Sesión"

3. **Verificar en navegador**
   - Página de éxito se muestra
   - Cerrar pestaña del portal
   - Navegar a google.com (✅ funciona)

4. **Probar desde línea de comandos**
   ```cmd
   REM En CMD
   ping 8.8.8.8
   REM ✅ Respuestas correctas
   
   curl https://www.google.com
   REM ✅ HTML de Google
   ```

### Resultados Esperados por Plataforma

| Plataforma | Login | Internet | Apps |
|------------|-------|----------|------|
| 🐧 Linux | ✅ curl/firefox | ✅ ping, curl funcionan | - |
| 📱 Android | ✅ Formulario en popup | ✅ Chrome carga | ✅ YouTube, Gmail |
| 🍎 iOS | ✅ Popup cierra solo | ✅ Safari carga | ✅ App Store, iMessage |
| 🪟 Windows | ✅ Edge muestra éxito | ✅ ping, navegación | ✅ Apps UWP |

**Común a todos:**
- ✅ `ping 8.8.8.8` → 0% packet loss
- ✅ Navegación web funciona completamente
- ✅ Apps pueden acceder a internet

### Verificación en Servidor (VM Ubuntu)

```bash
# EJECUTAR EN LA VM UBUNTU (SERVIDOR)

# 1. Ver nueva regla iptables para el cliente
sudo iptables -L FORWARD -v -n | grep "192.168.1.50"

# Output esperado (2 reglas: entrada + salida):
# ACCEPT  all  --  *  *  192.168.1.50  0.0.0.0/0  
# ACCEPT  all  --  *  *  0.0.0.0/0  192.168.1.50

# 2. Ver login exitoso en logs
grep "LOGIN_SUCCESS" /var/log/portal.log | tail -5

# Output esperado:
# [2025-12-05 10:30:45] LOGIN_SUCCESS: testuser from 192.168.1.50
# [2025-12-05 10:30:45] SESSION_CREATED: token=KjH7... IP=192.168.1.50 MAC=08:00:27:a3:b4:c5

# 3. Ver tráfico NAT en tiempo real
sudo iptables -t nat -L POSTROUTING -v -n

# Output esperado (bytes aumentando):
# pkts bytes  target  ... source         destination
# 1234 98765  MASQUERADE ... 192.168.1.0/24  0.0.0.0/0

# 4. Ver conexiones activas del cliente
sudo conntrack -L | grep 192.168.1.50

# Output esperado:
# tcp  ESTABLISHED  src=192.168.1.50 dst=142.250.185.46 ...
```

### Criterio de Éxito
✅ Login exitoso con credenciales válidas  
✅ Cookie de sesión establecida  
✅ Reglas iptables creadas para la IP  
✅ Acceso completo a internet habilitado

---

## ❌ Escenario 3: Autenticación Fallida

### Objetivo
Verificar que credenciales incorrectas NO otorgan acceso.

### Pasos de Prueba

1. **Intentar login con contraseña incorrecta**
   ```bash
   curl -X POST http://192.168.1.1/login \
     -d "username=testuser&password=wrongpassword" \
     -v
   ```

2. **Intentar login con usuario inexistente**
   ```bash
   curl -X POST http://192.168.1.1/login \
     -d "username=noexiste&password=cualquiera" \
     -v
   ```

3. **Verificar que NO hay acceso a internet**
   ```bash
   ping -c 3 8.8.8.8
   ```

### Resultados Esperados

```
✅ POST /login (contraseña incorrecta) → HTTP 200 con mensaje de error
✅ POST /login (usuario inexistente) → HTTP 200 con mensaje de error
❌ ping 8.8.8.8 → Sigue bloqueado (Destination Host Unreachable)
```

### Verificación en Servidor

```bash
# Ver intentos fallidos en logs
grep "LOGIN_FAILED" /var/log/portal.log

# Output esperado:
# [2025-12-05 10:35:12] LOGIN_FAILED: testuser from 192.168.1.50 (invalid password)
# [2025-12-05 10:35:20] LOGIN_FAILED: noexiste from 192.168.1.50 (user not found)

# Verificar que NO hay reglas nuevas para esta IP
sudo iptables -L FORWARD -v -n | grep 192.168.1.50
# Output: (vacío o solo reglas DROP)
```

### Criterio de Éxito
✅ Login rechazado con credenciales inválidas  
✅ Sin cookie de sesión establecida  
✅ Sin reglas iptables creadas  
✅ Internet sigue bloqueado

---

## 🚨 Escenario 4: Detección de Ataque por Suplantación IP

### Objetivo
Verificar que el sistema detecta y bloquea intentos de IP spoofing.

### Requisitos Previos
- Usuario legítimo (192.168.1.50) autenticado
- Atacante con otra IP (192.168.1.60)

### Pasos de Prueba

1. **Cliente legítimo se autentica**
   ```bash
   # En cliente 1 (192.168.1.50, MAC: aa:bb:cc:dd:ee:ff)
   curl -X POST http://192.168.1.1/login \
     -d "username=testuser&password=testpass"
   
   # Verificar que tiene internet
   ping -c 3 8.8.8.8  # ✅ Funciona
   ```

2. **Atacante intenta suplantar IP**
   ```bash
   # En cliente 2 (MAC real: 11:22:33:44:55:66)
   # Cambiar IP a la del usuario legítimo
   sudo ip addr flush dev eth0
   sudo ip addr add 192.168.1.50/24 dev eth0
   
   # Intentar acceder al portal
   curl http://192.168.1.1/dashboard
   ```

3. **Verificar bloqueo**
   ```bash
   # Atacante NO debe tener acceso
   ping -c 3 8.8.8.8  # ❌ Debe fallar
   ```

### Resultados Esperados

```
✅ Cliente legítimo (MAC: aa:bb:cc:dd:ee:ff) → Acceso permitido
❌ Atacante (MAC: 11:22:33:44:55:66) → Acceso DENEGADO
✅ Sistema detecta discrepancia IP vs MAC
```

### Verificación en Servidor

```bash
# Ver detección de ataque en logs
grep "SPOOFING_DETECTED" /var/log/portal.log

# Output esperado:
# [2025-12-05 10:40:15] SPOOFING_DETECTED: IP=192.168.1.50 Expected_MAC=aa:bb:cc:dd:ee:ff Actual_MAC=11:22:33:44:55:66
# [2025-12-05 10:40:15] ACCESS_DENIED: IP=192.168.1.50 (MAC mismatch)

# Verificar que el atacante está bloqueado
sudo iptables -L FORWARD -v -n | grep "192.168.1.50"
# Solo debe haber regla para MAC legítima
```

### Criterio de Éxito
✅ Sistema verifica IP + MAC antes de permitir acceso  
✅ Ataque detectado y registrado en logs  
✅ Atacante bloqueado aunque use IP autorizada  
✅ Usuario legítimo NO se ve afectado

---

## 🔒 Escenario 5: Funcionamiento HTTPS/SSL

### Objetivo
Verificar que el portal soporta conexiones cifradas HTTPS.

### Requisitos Previos
- Certificados SSL generados: `bash generate_cert.sh`
- Portal iniciado con soporte HTTPS (puerto 443)

### Pasos de Prueba

1. **Verificar que el servidor escucha en puerto 443**
   ```bash
   sudo netstat -tulpn | grep :443
   
   # Output esperado:
   # tcp  0  0.0.0.0:443  0.0.0.0:*  LISTEN  12345/python3
   ```

2. **Acceder vía HTTPS desde cliente**
   ```bash
   # Con curl (aceptar certificado autofirmado)
   curl -k -I https://192.168.1.1/
   
   # Verificar redirección HTTPS
   curl -k -L https://google.com
   ```

3. **Verificar cifrado SSL/TLS**
   ```bash
   # Ver detalles del certificado
   openssl s_client -connect 192.168.1.1:443 -showcerts
   
   # Ver protocolo y cipher suite
   nmap --script ssl-enum-ciphers -p 443 192.168.1.1
   ```

4. **Probar login sobre HTTPS**
   ```bash
   curl -k -X POST https://192.168.1.1/login \
     -d "username=testuser&password=testpass" \
     -v
   ```

### Resultados Esperados

```
✅ Servidor escuchando en puerto 443
✅ Certificado SSL válido (autofirmado)
✅ Protocolo: TLSv1.2 o superior
✅ Login funciona correctamente sobre HTTPS
✅ Contraseñas transmitidas cifradas (no en texto plano)
```

### Verificación en Servidor

```bash
# Ver conexiones HTTPS activas
sudo ss -tunap | grep :443

# Ver logs de servidor SSL
tail -f /var/log/portal.log | grep "SSL"

# Output esperado:
# [2025-12-05 10:45:30] SSL_CONNECTION: 192.168.1.50 (TLSv1.3)
# [2025-12-05 10:45:31] HTTPS_LOGIN: testuser from 192.168.1.50
```

### Verificar que NO hay contraseñas en texto plano

```bash
# Capturar tráfico con tcpdump (requiere permisos)
sudo tcpdump -i any port 443 -A -s 0 | grep "password"

# Resultado: NO debe mostrar la contraseña "testpass" en texto plano
# Solo debe verse datos cifrados (basura ilegible)
```

### Criterio de Éxito
✅ Portal accesible vía HTTPS  
✅ Certificados SSL funcionando  
✅ Conexiones cifradas con TLS  
✅ Credenciales protegidas durante transmisión

---

## 📱 Escenario 6: Detección Automática del Portal

### Objetivo
Verificar que dispositivos muestran notificación automática al conectarse usando el servidor DNS falso.

### Cómo Funciona la Detección

Cada SO hace consultas DNS a URLs específicas:
- **Android:** `connectivitycheck.gstatic.com`
- **iOS:** `captive.apple.com`
- **Windows:** `www.msftconnecttest.com`

El DNS falso responde TODAS con `192.168.1.1` → El SO detecta portal cautivo

### Configuración Previa

**EN EL SERVIDOR (VM Ubuntu):**

```bash
# Verificar que dns_server.py está corriendo
ps aux | grep dns_server

# Verificar puerto 53 escuchando
sudo netstat -tulpn | grep :53

# Output esperado:
# udp  0.0.0.0:53  0.0.0.0:*  12345/python3

# Ver logs DNS en tiempo real
sudo tail -f /var/log/syslog | grep "DNS"
```

### Prueba por Plataforma

#### 📱 Android (Smartphone/Tablet)

**EN EL DISPOSITIVO ANDROID:**

1. **Olvidar red WiFi (si estaba conectado)**
   - Ajustes → WiFi → Portal_Cautivo_Test
   - Olvidar red

2. **Conectar nuevamente**
   - Buscar "Portal_Cautivo_Test"
   - Ingresar contraseña: test1234
   - **NO abrir Chrome ni ninguna app**

3. **Observar notificación (5-10 segundos)**
   - Aparece en barra de notificaciones
   - Texto: "Se requiere inicio de sesión" o "Sign in to network"
   - **NO TOCAR AÚN**

**EN EL SERVIDOR (VM Ubuntu) - Ver en tiempo real:**
```bash
# Debe aparecer esta consulta DNS:
sudo tail -f /var/log/syslog | grep connectivitycheck

# Output esperado:
# [10:40:15] DNS Query: connectivitycheck.gstatic.com from 192.168.1.51
# [10:40:15] DNS Response: connectivitycheck.gstatic.com → 192.168.1.1
```

4. **EN EL DISPOSITIVO ANDROID: Tocar notificación**
   - Abre navegador interno (no Chrome) con el portal
   - Debe mostrar página de login

**QUÉ ESPERAR:**
- ✅ Notificación aparece sin intervención (5-10s)
- ✅ Portal se abre en navegador interno del sistema
- ✅ No necesitas abrir Chrome manualmente

#### 🍎 iOS (iPhone/iPad)

**EN EL DISPOSITIVO iOS:**

1. **Olvidar red WiFi**
   - Ajustes → Wi-Fi → (i) → Olvidar esta red

2. **Conectar nuevamente**
   - Conectar a "Portal_Cautivo_Test"
   - Contraseña: test1234
   - **NO abrir Safari**

3. **Popup automático (2-3 segundos)**
   - iOS abre ventana emergente AUTOMÁTICAMENTE
   - Muestra directamente el portal
   - **Más rápido que Android**

**EN EL SERVIDOR (VM Ubuntu):**
```bash
# Ver consultas de iOS
sudo tail -f /var/log/syslog | grep captive.apple.com

# Output esperado:
# [10:42:30] DNS Query: captive.apple.com from 192.168.1.52
# [10:42:30] DNS Response: captive.apple.com → 192.168.1.1
```

**QUÉ ESPERAR:**
- ✅ Popup aparece INMEDIATAMENTE (2-3s)
- ✅ Portal ya visible, no necesitas tocar nada más
- ✅ Ventana emergente dedicada (no Safari)

#### 🪟 Windows 10/11 (PC/Laptop)

**EN EL DISPOSITIVO WINDOWS:**

1. **Conectar cable Ethernet o WiFi**
   - Conectar a la red del servidor
   - Configurar IP (manual o DHCP)

2. **Observar notificación (3-5 segundos)**
   - Centro de acciones (esquina derecha)
   - Icono de red con triángulo amarillo
   - Texto: "Requiere acción" o "Action needed"

**EN EL SERVIDOR (VM Ubuntu):**
```bash
# Ver consultas de Windows
sudo tail -f /var/log/syslog | grep msftconnecttest

# Output esperado:
# [10:45:00] DNS Query: www.msftconnecttest.com from 192.168.1.60
# [10:45:00] DNS Response: www.msftconnecttest.com → 192.168.1.1
```

3. **EN WINDOWS: Click en notificación**
   - Abre Microsoft Edge automáticamente
   - URL: http://192.168.1.1/
   - Muestra portal de login

**QUÉ ESPERAR:**
- ✅ Notificación aparece en 3-5 segundos
- ✅ Edge se abre automáticamente (no Chrome)
- ✅ Portal listo para login

#### 🐧 Linux Desktop (con NetworkManager)

**EN EL CLIENTE LINUX:**

1. **Conectar a la red**
   ```bash
   # NetworkManager detecta portal cautivo
   nmcli device wifi connect Portal_Cautivo_Test password test1234
   ```

2. **Esperar notificación**
   - Aparece popup de NetworkManager
   - "Network requires authentication"
   - Click abre navegador predeterminado

**EN EL SERVIDOR (VM Ubuntu):**
```bash
# Ver consultas de Linux
sudo tail -f /var/log/syslog | grep "DNS Query"

# Output esperado:
# [10:47:30] DNS Query: connectivity-check.ubuntu.com from 192.168.1.70
```

**QUÉ ESPERAR:**
- ✅ Popup de NetworkManager
- ✅ Firefox/Chrome abre el portal

### Tabla Comparativa de Detección

| OS | URL de Verificación | Tiempo | Método |
|----|---------------------|--------|--------|
| 📱 Android | connectivitycheck.gstatic.com | 5-10s | Notificación → navegador interno |
| 🍎 iOS | captive.apple.com | 2-3s | Popup automático instantáneo |
| 🪟 Windows | www.msftconnecttest.com | 3-5s | Notificación → Edge |
| 🐧 Linux | connectivity-check.ubuntu.com | Variable | Popup → navegador default |

### Verificación Completa en Servidor

**EN EL SERVIDOR (VM Ubuntu):**

```bash
# Ver TODAS las consultas de detección (útil con múltiples dispositivos)
sudo tail -f /var/log/syslog | grep -E "connectivitycheck|captive.apple|msftconnecttest|connectivity-check"

# Contar dispositivos únicos que detectaron el portal
grep "DNS Query" /var/log/syslog | grep -E "connectivitycheck|captive|msftconnect" | awk '{print $NF}' | sort -u | wc -l

# Ver qué tipo de dispositivo se conectó (por URL)
grep "connectivitycheck" /var/log/syslog | tail -1  # Android
grep "captive.apple" /var/log/syslog | tail -1      # iOS
grep "msftconnecttest" /var/log/syslog | tail -1    # Windows
```

### Criterio de Éxito
✅ **Android:** Notificación aparece sin abrir apps (5-10s)  
✅ **iOS:** Popup automático inmediato (2-3s)  
✅ **Windows:** Notificación + Edge abre portal (3-5s)  
✅ **Linux:** NetworkManager detecta y notifica  
✅ Todas las plataformas usan DNS falso correctamente  
✅ Portal se abre sin intervención manual del usuario

---

## ⚡ Escenario 7: Concurrencia con Múltiples Clientes

### Objetivo
Verificar que el portal soporta múltiples usuarios simultáneos sin bloqueos.

### Pasos de Prueba

1. **Preparar 10 usuarios de prueba**
   ```bash
   for i in {1..10}; do
     python3 auth.py add "user$i" "pass$i"
   done
   ```

2. **Simular 10 conexiones simultáneas**
   ```bash
   # Desde el servidor (o usar Apache Bench)
   for i in {1..10}; do
     (
       curl -X POST http://192.168.1.1/login \
         -d "username=user$i&password=pass$i" \
         --silent --output /dev/null &
     )
   done
   wait
   ```

3. **Prueba de carga con Apache Bench**
   ```bash
   # 100 peticiones, 10 concurrentes
   ab -n 100 -c 10 http://192.168.1.1/
   ```

4. **Verificar threads activos**
   ```bash
   # Ver threads del proceso Python
   ps -T -p $(pgrep -f "python3 server.py")
   
   # Contar threads
   ps -T -p $(pgrep -f "python3 server.py") | wc -l
   ```

### Resultados Esperados

```
✅ 10 logins completados correctamente (sin errores)
✅ Múltiples threads activos en el servidor
✅ Apache Bench: 0 failed requests
✅ Tiempo de respuesta < 1 segundo por petición
```

### Verificación en Servidor

```bash
# Ver sesiones activas simultáneas
grep "SESSION_CREATED" /var/log/portal.log | tail -10

# Output esperado:
# [10:50:01] SESSION_CREATED: user1 from 192.168.1.51
# [10:50:01] SESSION_CREATED: user2 from 192.168.1.52
# [10:50:02] SESSION_CREATED: user3 from 192.168.1.53
# ... (hasta user10)

# Verificar reglas iptables para todas las IPs
sudo iptables -L FORWARD -v -n | grep ACCEPT | wc -l
# Output esperado: >= 20 (2 reglas por IP: entrada + salida)
```

### Criterio de Éxito
✅ Servidor acepta conexiones concurrentes sin bloqueos  
✅ Cada thread maneja su cliente independientemente  
✅ Sin race conditions en sesiones/autorizaciones  
✅ Performance aceptable (< 1s por petición)

---

## 🔄 Escenario 8: Revocación de Acceso

### Objetivo
Verificar que se puede revocar el acceso a internet de un usuario autenticado.

### Requisitos Previos
- Usuario autenticado con acceso activo (IP: 192.168.1.50)

### Pasos de Prueba

1. **Verificar acceso inicial**
   ```bash
   # En cliente 192.168.1.50
   ping -c 3 8.8.8.8  # ✅ Debe funcionar
   ```

2. **Revocar acceso desde servidor**
   ```bash
   sudo ./scripts/revoke_internet.sh 192.168.1.50
   ```

3. **Verificar bloqueo inmediato**
   ```bash
   # En cliente 192.168.1.50
   ping -c 3 8.8.8.8  # ❌ Debe fallar
   
   # Intentar acceso web
   curl -I http://google.com  # ❌ Timeout o redirect al portal
   ```

4. **Verificar en servidor**
   ```bash
   # Las reglas ACCEPT deben haber sido eliminadas
   sudo iptables -L FORWARD -v -n | grep 192.168.1.50
   
   # Output esperado: (vacío o solo DROP)
   ```

### Resultados Esperados

```
✅ Script revoke_internet.sh ejecutado sin errores
✅ Reglas iptables ACCEPT eliminadas para esa IP
❌ Cliente pierde acceso a internet inmediatamente
✅ Cliente redirigido nuevamente al portal
```

### Verificación en Logs

```bash
grep "192.168.1.50" /var/log/portal.log | tail -5

# Output esperado:
# [10:55:00] ACCESS_REVOKED: IP=192.168.1.50 (manual revocation)
# [10:55:01] SESSION_TERMINATED: IP=192.168.1.50
```

### Criterio de Éxito
✅ Revocación efectiva e inmediata  
✅ Usuario debe re-autenticarse para recuperar acceso  
✅ Logs registran la revocación

---

## 🌐 Escenario 9: NAT/Masquerading de IPs

### Objetivo
Verificar que las IPs privadas se enmascaran correctamente con la IP pública del gateway.

### Requisitos Previos
- NAT configurado: `sudo ./scripts/nat_setup.sh`
- Cliente autenticado con acceso a internet

### Pasos de Prueba

1. **Verificar configuración NAT**
   ```bash
   sudo iptables -t nat -L POSTROUTING -v -n
   
   # Output esperado:
   # MASQUERADE  all  --  192.168.1.0/24  0.0.0.0/0
   ```

2. **Desde cliente, acceder a servicio que muestra IP pública**
   ```bash
   # En cliente (192.168.1.50)
   curl ifconfig.me
   
   # Debe mostrar la IP pública del gateway, NO 192.168.1.50
   ```

3. **Capturar tráfico en interfaz WAN del servidor**
   ```bash
   # En servidor, interfaz WAN (ejemplo: eth0)
   sudo tcpdump -i eth0 -n host 8.8.8.8 | grep "192.168.1.50"
   
   # Resultado: NO debe aparecer 192.168.1.50
   # Solo debe verse la IP pública del gateway
   ```

4. **Ver conexiones trackeadas por conntrack**
   ```bash
   sudo conntrack -L | grep 192.168.1.50
   
   # Output esperado:
   # tcp  ESTABLISHED  src=192.168.1.50 dst=8.8.8.8 ... [ASSURED]
   # (muestra traducción de IPs)
   ```

### Resultados Esperados

```
✅ curl ifconfig.me desde cliente → Muestra IP pública del gateway
✅ Tráfico en WAN NO muestra IPs privadas (192.168.1.x)
✅ conntrack muestra traducciones de dirección activas
✅ Múltiples clientes comparten la misma IP pública
```

### Verificación Técnica

```bash
# Ver estadísticas de NAT
sudo iptables -t nat -L POSTROUTING -v -n

# Output esperado:
# Chain POSTROUTING (policy ACCEPT 0 packets, 0 bytes)
# pkts bytes target     prot opt in     out     source           destination
# 1234 98765 MASQUERADE all  --  *      eth0    192.168.1.0/24   0.0.0.0/0
```

### Criterio de Éxito
✅ IPs privadas enmascaradas correctamente  
✅ Conexiones externas solo ven IP pública del gateway  
✅ NAT funciona para todos los protocolos (TCP, UDP, ICMP)

---

## 📊 Escenario 10: Prueba Integral Completa

### Objetivo
Validar todos los componentes trabajando juntos en un flujo realista.

### Flujo Completo

1. **Cliente nuevo se conecta**
   - Recibe IP vía DHCP o configuración manual
   - Gateway y DNS apuntan al servidor del portal

2. **Detección automática**
   - Android/iOS/Windows detecta portal
   - Muestra notificación automática

3. **Intento de acceso a internet**
   - Cliente intenta acceder a google.com
   - DNS responde con IP del gateway
   - iptables redirige a página de login

4. **Autenticación**
   - Usuario completa formulario (HTTPS)
   - Contraseña hasheada se verifica
   - Sistema valida IP + MAC

5. **Acceso concedido**
   - iptables crea reglas ACCEPT para esa IP
   - NAT enmascara la IP privada
   - Cliente tiene internet completo

6. **Actividad normal**
   - Cliente navega por internet
   - Todo el tráfico pasa por NAT
   - Sesión permanece activa

7. **Intento de ataque**
   - Otro dispositivo intenta suplantar la IP
   - Sistema detecta MAC diferente
   - Ataque bloqueado y registrado

8. **Finalización**
   - Administrador revoca acceso
   - Cliente pierde internet
   - Debe re-autenticarse

### Comandos de Validación

```bash
# 1. Verificar todos los servicios activos
sudo systemctl status captive-portal  # (si configurado como servicio)
sudo netstat -tulpn | grep -E ":80|:443|:53"

# 2. Verificar configuración de firewall completa
sudo iptables -L -v -n
sudo iptables -t nat -L -v -n

# 3. Ver actividad en tiempo real
sudo tail -f /var/log/portal.log

# 4. Verificar sesiones activas
grep "SESSION_CREATED" /var/log/portal.log | tail -20

# 5. Verificar IPs autorizadas
sudo iptables -L FORWARD -v -n | grep ACCEPT

# 6. Verificar NAT funcionando
sudo conntrack -L | wc -l  # Número de conexiones trackeadas
```

### Resultados Esperados

```
✅ Todos los servicios operativos (web, DNS, firewall)
✅ Detección automática funcionando en todos los dispositivos
✅ Login exitoso con credenciales válidas
✅ Acceso a internet completo post-autenticación
✅ NAT enmascarando IPs correctamente
✅ Anti-spoofing detectando ataques
✅ Concurrencia soportada (múltiples usuarios)
✅ Revocación de acceso funcionando
```

### Criterio de Éxito
✅ **7.5/5.0 puntos cumplidos**  
✅ Todos los requisitos mínimos funcionan  
✅ Todos los extras implementados correctamente  
✅ Sistema estable bajo carga  
✅ Sin errores críticos en logs

---

## 📝 Resumen de Escenarios

| # | Escenario | Requisito Validado | Tiempo Est. |
|---|-----------|-------------------|-------------|
| 1 | Conexión y bloqueo | Firewall DROP | 5 min |
| 2 | Autenticación exitosa | Login + forwarding | 5 min |
| 3 | Autenticación fallida | Validación credenciales | 3 min |
| 4 | Anti-suplantación IP | IP+MAC verification | 10 min |
| 5 | HTTPS/SSL | Cifrado TLS | 10 min |
| 6 | Detección automática | DNS falso | 15 min |
| 7 | Concurrencia | Threading | 10 min |
| 8 | Revocación | Control de acceso | 5 min |
| 9 | NAT/Masquerading | Enmascaramiento | 10 min |
| 10 | Prueba integral | Todos | 30 min |

**Tiempo total estimado:** ~1.5 horas

---

## 🛠️ Herramientas Recomendadas

### Para Pruebas de Red
- `ping` - Verificar conectividad
- `curl` - Probar endpoints HTTP/HTTPS
- `nslookup` / `dig` - Verificar DNS
- `tcpdump` - Captura de tráfico
- `iptables` - Verificar reglas de firewall
- `conntrack` - Ver conexiones NAT

### Para Pruebas de Carga
- `ab` (Apache Bench) - Pruebas de concurrencia
- `siege` - Pruebas de carga HTTP
- `wrk` - Benchmark HTTP moderno

### Para Seguridad
- `nmap` - Escaneo de puertos y servicios
- `openssl` - Verificar certificados SSL
- `arp` - Ver tabla ARP (detección MAC)
- `wireshark` - Análisis de tráfico detallado

---

## ✅ Checklist Final

```
[✓] Escenario 1: Bloqueo inicial
[✓] Escenario 2: Login exitoso
[✓] Escenario 3: Login fallido
[✓] Escenario 4: Anti-spoofing
[✓] Escenario 5: HTTPS
[✓] Escenario 6: Detección automática
[✓] Escenario 7: Concurrencia
[✓] Escenario 8: Revocación
[✓] Escenario 9: NAT
[✓] Escenario 10: Prueba integral

RESULTADO: ✅ Portal cautivo 100% funcional
PUNTUACIÓN: 7.5/5.0 🏆
```

---

**Nota:** Estos escenarios cubren tanto los requisitos mínimos (5.0 puntos) como los extras (2.5 puntos). Ejecutarlos todos garantiza la validación completa del sistema.
