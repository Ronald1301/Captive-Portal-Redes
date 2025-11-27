# 🔧 Configuración para Pruebas con VirtualBox

## 📱 Tu Escenario Específico

- **Teléfono**: Hotspot WiFi proporcionando internet
- **PC Windows**: Laptop conectada al hotspot del teléfono  
- **VM Linux (VirtualBox)**: Ejecuta el portal cautivo
- **Dispositivos de prueba**: Tu teléfono Y tu PC Windows

```
┌─────────────┐
│  Teléfono   │  📱 Hotspot WiFi (ej: 192.168.43.1)
│  (Hotspot)  │      Proporciona internet
└──────┬──────┘
       │
       │ WiFi
       │
┌──────▼────────────────────────────────────┐
│         PC Windows (Laptop)                │
│  📶 WiFi: 192.168.43.X (Red del hotspot)  │
│  ├─ Adaptador WiFi recibe internet        │
│  └─ VirtualBox instalado                  │
│                                            │
│  ┌──────────────────────────────────┐    │
│  │  VM Linux (Ubuntu/Debian)        │    │
│  │  🌐 Portal Cautivo               │    │
│  │  IP: 192.168.43.Y (misma red)    │    │
│  └──────────────────────────────────┘    │
└───────────────────────────────────────────┘
```

**Objetivo**: Que tanto tu teléfono como tu PC puedan acceder al portal cautivo en `http://192.168.43.Y`

---

## 📋 PASO 1: Preparar la Red del Teléfono

### 1.1 Activar Hotspot en tu Teléfono

1. **Activa el hotspot WiFi** en tu teléfono
2. **Configura el hotspot**:
   - Nombre de red: Cualquiera (ej: "Mi_Hotspot")
   - Contraseña: Ponle una contraseña
   - **Banda**: Preferiblemente 2.4 GHz (mejor compatibilidad)
3. **Anota el nombre de la red** - lo necesitarás después

### 1.2 Obtener la IP del Teléfono (Gateway)

**En Android**:
- Ve a: **Ajustes** → **Conexiones** → **Hotspot y anclaje** → **Hotspot móvil** 
- O busca "Hotspot" en ajustes
- Verás algo como: "Red creada: 192.168.43.1" o similar
- **ANOTA ESTA IP** → Esta es tu **IP Gateway**

**En iPhone**:
- Generalmente el iPhone usa: **172.20.10.1**
- Puedes verificarlo desde tu PC después de conectarte

📝 **Anota aquí**:
- IP del teléfono (Gateway): `_________________` (ej: 192.168.43.1)

---

## 🪟 PASO 2: Conectar y Configurar Windows

### 2.1 Conectar tu PC al Hotspot

1. En tu PC Windows, conéctate a la red WiFi del teléfono
2. Espera a que se conecte correctamente

### 2.2 Obtener las IPs de Windows

Abre **PowerShell** (no hace falta admin por ahora) y ejecuta:

```powershell
ipconfig /all
```

**Busca el adaptador WiFi** (puede llamarse "Wi-Fi", "WLAN", "Wireless Network Connection"):

```
Adaptador de LAN inalámbrica Wi-Fi:
   ...
   Dirección IPv4. . . . . . . . . : 192.168.43.5
   Máscara de subred . . . . . . . : 255.255.255.0
   Puerta de enlace predeterminada : 192.168.43.1
```

📝 **Anota ESTOS VALORES**:
- **IP de Windows**: `_________________` (ej: 192.168.43.5)
- **Máscara de subred**: `_________________` (ej: 255.255.255.0)
- **Gateway** (debe coincidir con IP del teléfono): `_________________` (ej: 192.168.43.1)
- **Rango de red**: `_________________` (ej: 192.168.43.0/24)

**¿Cómo identificar el adaptador correcto?**
- Busca el que tiene "Descripción" con palabras como: **WiFi**, **Wireless**, **802.11**, o la marca de tu tarjeta WiFi (Intel, Realtek, etc.)
- Verifica que tenga una dirección IPv4 en el rango del hotspot

### 2.3 Identificar el Nombre del Adaptador de Red

Ejecuta en PowerShell:

```powershell
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object Name, InterfaceDescription, Status
```

**Busca tu adaptador WiFi** y anota el **Name** (ej: "Wi-Fi", "WLAN"):

📝 **Anota el nombre del adaptador**:
- Nombre del adaptador WiFi en Windows: `_________________` (ej: "Wi-Fi")

---

## 🖥️ PASO 3: Configurar VirtualBox

### 3.1 Configuración de Red de la VM (MODO BRIDGED - Recomendado)

Este es el modo más simple y directo para tu escenario.

1. **Abre VirtualBox**
2. **Selecciona tu VM** (pero NO la inicies aún)
3. Click derecho → **Configuración** (o botón "Configuración")
4. Ve a la sección **Red**

#### Configurar Adaptador 1:

- ☑️ **Habilitar adaptador de red**
- **Conectado a**: Selecciona **Adaptador puente** (Bridged Adapter)
- **Nombre**: Selecciona tu adaptador WiFi de Windows 
  - Busca el que coincida con el nombre que anotaste
  - Ejemplo: "Intel(R) Wi-Fi 6 AX201 160MHz" o similar
  - ⚠️ **MUY IMPORTANTE**: Selecciona el adaptador que está conectado al hotspot del teléfono
- **Modo promiscuo**: Selecciona **Permitir todo**
- **Tipo de adaptador**: PCnet-FAST III (o paravirtualizado si tienes guest additions)

5. **Guarda** los cambios (Click en "Aceptar")

### 3.2 Iniciar la VM

1. **Inicia tu VM Linux**
2. Espera a que arranque completamente
3. Inicia sesión

---

## 🐧 PASO 4: Configurar la VM Linux

### 4.1 Identificar la Interfaz de Red en Linux

Dentro de tu VM Linux, abre una terminal y ejecuta:

```bash
ip addr show
```

**Busca tu interfaz de red** (puede ser `eth0`, `enp0s3`, `ens33`, etc.):

```bash
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP
    inet 192.168.43.XXX/24 brd 192.168.43.255 scope global dynamic enp0s3
```

📝 **Anota**:
- **Nombre de la interfaz**: `_________________` (ej: enp0s3, eth0)
- **IP actual de la VM**: `_________________` (ej: 192.168.43.100)

### 4.2 Asignar una IP Estática a la VM (IMPORTANTE)

Para que el portal sea accesible de forma consistente, necesitas una **IP fija**.

#### Opción A: Usando Netplan (Ubuntu 18.04+)

1. Edita el archivo de configuración:

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

2. Modifica el contenido (ajusta los valores según tu red):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:  # ← Reemplaza con el nombre de tu interfaz
      dhcp4: no
      addresses:
        - 192.168.43.100/24  # ← IP fija para tu VM (debe estar en el rango del hotspot)
      gateway4: 192.168.43.1  # ← IP de tu teléfono (gateway)
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

3. Aplica los cambios:

```bash
sudo netplan apply
```

#### Opción B: Usando /etc/network/interfaces (Debian/Ubuntu antiguo)

1. Edita el archivo:

```bash
sudo nano /etc/network/interfaces
```

2. Agrega o modifica:

```bash
auto enp0s3  # ← Tu interfaz
iface enp0s3 inet static
    address 192.168.43.100  # ← IP fija para tu VM
    netmask 255.255.255.0
    gateway 192.168.43.1    # ← IP de tu teléfono
    dns-nameservers 8.8.8.8 8.8.4.4
```

3. Reinicia el networking:

```bash
sudo systemctl restart networking
```

#### Opción C: Usando nmcli (NetworkManager)

```bash
# Listar conexiones
nmcli con show

# Configurar IP estática (ajusta los valores)
sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.43.100/24
sudo nmcli con mod "Wired connection 1" ipv4.gateway 192.168.43.1
sudo nmcli con mod "Wired connection 1" ipv4.dns "8.8.8.8 8.8.4.4"
sudo nmcli con mod "Wired connection 1" ipv4.method manual

# Reiniciar la conexión
sudo nmcli con down "Wired connection 1"
sudo nmcli con up "Wired connection 1"
```

### 4.3 Verificar la Conexión

```bash
# Verificar IP
ip addr show

# Hacer ping al gateway (teléfono)
ping -c 4 192.168.43.1

# Hacer ping a internet
ping -c 4 8.8.8.8
```

📝 **Anota la IP final de tu VM**:
- **IP de la VM Linux**: `_________________` (ej: 192.168.43.100)

---

## 🔥 PASO 5: Configurar Firewall en Windows

### 5.1 Abrir PowerShell como Administrador

1. Presiona **Win + X**
2. Selecciona **Windows PowerShell (Administrador)** o **Terminal (Administrador)**
3. Click en "Sí" cuando pida permisos

### 5.2 Crear Reglas de Firewall

Ejecuta estos comandos para permitir que tu teléfono y PC accedan al portal:

```powershell
# Permitir tráfico HTTP (puerto 80)
New-NetFirewallRule -DisplayName "Captive Portal HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# Permitir tráfico HTTPS (puerto 443)
New-NetFirewallRule -DisplayName "Captive Portal HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Permitir tráfico DNS (puerto 53)
New-NetFirewallRule -DisplayName "Captive Portal DNS" -Direction Inbound -Protocol UDP -LocalPort 53 -Action Allow
```

**Nota**: Aunque el portal corre en la VM, estas reglas ayudan a que Windows no bloquee el tráfico que pasa a través de él.

---

## 🚀 PASO 6: Configurar y Ejecutar el Portal Cautivo

### 6.1 Navegar al Directorio del Proyecto

En la VM Linux:

```bash
cd ~/captive-portal  # O la ruta donde clonaste el proyecto
ls -la  # Verificar que estás en el directorio correcto
```

### 6.2 Configurar Variables de Entorno (IMPORTANTE)

Necesitas decirle al portal qué interfaz de red usar:

```bash
# Editar el script de inicio
nano scripts/start_captive_portal.sh
```

**Verifica o modifica estas líneas**:
- `LAN_IF`: Tu interfaz de red (ej: `enp0s3`)
- `CAPTIVE_IFACE`: Debe ser la misma interfaz

Ejemplo:

```bash
LAN_IF="enp0s3"  # ← Tu interfaz
CAPTIVE_IFACE="enp0s3"  # ← La misma interfaz
```

### 6.3 Crear Usuarios para Pruebas

```bash
# Crear un usuario de prueba
python3 auth.py add testuser password123

# Ver usuarios creados
python3 auth.py list
```

### 6.4 Generar Certificados SSL (Opcional pero Recomendado)

```bash
chmod +x generate_cert.sh
./generate_cert.sh
```

Cuando te pregunte el **Common Name**, ingresa la IP de tu VM: `192.168.43.100`

### 6.5 Iniciar el Portal Cautivo

```bash
# Dar permisos de ejecución
chmod +x scripts/*.sh

# Iniciar el portal
sudo ./scripts/start_captive_portal.sh
```

**Deberías ver**:

```text
🚀 Iniciando Portal Cautivo...
✅ Configurando iptables...
✅ Servidor DNS iniciado en puerto 53
✅ Servidor HTTP iniciado en puerto 80
✅ Servidor HTTPS iniciado en puerto 443
🌐 Portal Cautivo activo en: https://192.168.43.100
```

📝 **Anota la URL del portal**:

- URL del portal: `http://192.168.43.100` o `https://192.168.43.100`

---

## 📱 PASO 7: Probar desde los Dispositivos

### 7.1 Probar desde el PC Windows

1. **Abre tu navegador** (Chrome, Edge, Firefox)
2. **Navega a**: `http://192.168.43.100` (reemplaza con la IP de tu VM)
3. **Deberías ver** la página de login del portal cautivo
4. **Inicia sesión**:
   - Usuario: `testuser`
   - Contraseña: `password123`
5. **Verifica** que te redirija a la página de éxito

**Si usas HTTPS**: `https://192.168.43.100`

- El navegador mostrará advertencia de certificado (es normal con certificados autofirmados)
- Click en **Avanzado** → **Continuar al sitio** (o similar)

### 7.2 Probar desde el Teléfono

#### Método 1: Acceso Directo

1. **Desactiva los datos móviles** del teléfono (usa solo WiFi del hotspot)
2. **Abre el navegador** en tu teléfono
3. **Navega a**: `http://192.168.43.100`
4. **Inicia sesión** con las mismas credenciales

#### Método 2: Detección Automática (Portal Cautivo)

1. **Mantén datos móviles desactivados**
2. **Intenta navegar a cualquier sitio**: `http://www.google.com`
3. **El portal cautivo debería interceptar** y redirigirte automáticamente
4. **Inicia sesión**

**Nota para Android**: 

- Android detecta portales cautivos automáticamente
- Puede mostrar una notificación "Inicia sesión en la red"

**Nota para iPhone**:

- Similar a Android, mostrará una ventana emergente automática

---

## 📊 PASO 8: Verificar que Todo Funciona

### 8.1 En la VM Linux (Ver logs)

Mientras el portal está corriendo, verás logs en la terminal:

```text
[INFO] Nueva conexión desde 192.168.43.5:54321
[INFO] Solicitud GET / desde 192.168.43.5
[INFO] Login exitoso: usuario 'testuser' desde 192.168.43.5
[INFO] MAC detectada: aa:bb:cc:dd:ee:ff
```

### 8.2 Verificar Usuarios Autenticados

En otra terminal de la VM:

```bash
# Ver sesiones activas (si implementaste este feature)
# O revisar los logs del servidor
```

### 8.3 Verificar iptables

```bash
# Ver reglas de iptables
sudo iptables -L -n -v

# Deberías ver las reglas del portal cautivo
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema 1: No puedo acceder al portal desde Windows/Teléfono

**Causa posible**: Firewall o configuración de red

**Soluciones**:

#### a) Verificar que la VM tenga la IP correcta

```bash
ip addr show
ping -c 4 192.168.43.1  # Ping al gateway (teléfono)
```

#### b) Verificar que el servidor esté corriendo

```bash
# Ver si los puertos están abiertos
sudo netstat -tuln | grep -E ':(80|443|53)'
```

Deberías ver:

```text
tcp    0    0 0.0.0.0:80    0.0.0.0:*    LISTEN
tcp    0    0 0.0.0.0:443   0.0.0.0:*    LISTEN
udp    0    0 0.0.0.0:53    0.0.0.0:*
```

#### c) Probar conectividad desde Windows

Abre PowerShell en Windows:

```powershell
# Ping a la VM
ping 192.168.43.100

# Verificar puerto HTTP
Test-NetConnection -ComputerName 192.168.43.100 -Port 80

# Verificar puerto HTTPS
Test-NetConnection -ComputerName 192.168.43.100 -Port 443
```

Si el ping no funciona:

- Verifica que ambos dispositivos estén en la misma red
- Verifica el firewall de la VM Linux

```bash
# Desactivar temporalmente el firewall en Linux para probar
sudo ufw disable

# O abrir puertos específicos
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 53/udp
sudo ufw enable
```

### Problema 2: El teléfono no detecta el portal automáticamente

**Soluciones**:

#### a) Asegúrate de que el DNS falso esté corriendo

```bash
# En la VM, verificar que dns_server.py esté corriendo
ps aux | grep dns_server.py
```

#### b) Configura el DNS manualmente en el teléfono

**En Android**:

1. Ve a **Ajustes** → **WiFi**
2. Mantén presionado tu hotspot → **Modificar red**
3. **Opciones avanzadas** → **Configuración IP**: **Estática**
4. **DNS 1**: `192.168.43.100` (IP de tu VM)
5. **Guardar**

**En iPhone**:

1. Ve a **Ajustes** → **WiFi**
2. Toca la (i) junto a tu red
3. **Configurar DNS** → **Manual**
4. Elimina los DNS existentes
5. Agrega: `192.168.43.100`

#### c) Acceso manual

Simplemente navega directamente a `http://192.168.43.100`

### Problema 3: La VM no tiene internet

**Soluciones**:

#### a) Verificar gateway y DNS

```bash
# Ver la tabla de rutas
ip route show

# Debería mostrar:
# default via 192.168.43.1 dev enp0s3
```

#### b) Verificar DNS

```bash
cat /etc/resolv.conf

# Debería contener:
# nameserver 8.8.8.8
```

#### c) Reiniciar networking

```bash
sudo systemctl restart networking
# o
sudo systemctl restart NetworkManager
```

### Problema 4: Certificado SSL no funciona

**Soluciones**:

#### a) Regenerar certificados

```bash
./generate_cert.sh
```

Usa la IP de tu VM como Common Name: `192.168.43.100`

#### b) Usa HTTP en lugar de HTTPS (para pruebas)

Simplemente accede a `http://192.168.43.100`

### Problema 5: "Connection refused" o "ERR_CONNECTION_REFUSED"

**Causa**: El servidor no está escuchando o el firewall está bloqueando

**Soluciones**:

#### a) Verificar que el servidor esté corriendo

```bash
sudo systemctl status captive-portal  # Si lo configuraste como servicio
# o
ps aux | grep server.py
```

#### b) Reiniciar el portal

```bash
sudo ./scripts/stop_captive_portal.sh
sudo ./scripts/start_captive_portal.sh
```

#### c) Verificar permisos

```bash
# Los puertos 80, 443 y 53 requieren privilegios de root
# Asegúrate de ejecutar con sudo
```

---

## 📝 RESUMEN DE IPs Y CONFIGURACIÓN

Completa esta tabla con tus valores reales:

| Dispositivo | IP | Función |
|-------------|-------|---------|
| **Teléfono (Gateway)** | `192.168.43.1` | Hotspot WiFi - Proveedor de internet |
| **PC Windows** | `192.168.43.5` | Cliente - Dispositivo de prueba |
| **VM Linux** | `192.168.43.100` | Servidor - Portal Cautivo |
| **Red/Máscara** | `192.168.43.0/24` | Rango de red del hotspot |

**URL del Portal**: `http://192.168.43.100` o `https://192.168.43.100`

**Credenciales de prueba**:

- Usuario: `testuser`
- Contraseña: `password123`

---

## 🎯 CHECKLIST FINAL

Antes de probar, verifica que hayas completado:

- [ ] ✅ Teléfono: Hotspot activado y funcionando
- [ ] ✅ PC Windows: Conectado al hotspot del teléfono
- [ ] ✅ Windows: Identificaste la IP del adaptador WiFi
- [ ] ✅ VirtualBox: Configurado en modo Bridged con adaptador WiFi correcto
- [ ] ✅ VM Linux: Arrancada y con IP estática configurada
- [ ] ✅ VM Linux: Puede hacer ping al gateway (teléfono)
- [ ] ✅ VM Linux: Tiene acceso a internet
- [ ] ✅ Portal: Configurado con la interfaz de red correcta
- [ ] ✅ Portal: Usuario de prueba creado
- [ ] ✅ Portal: Servidor corriendo (puertos 80, 443, 53 escuchando)
- [ ] ✅ Windows: Puede hacer ping a la VM
- [ ] ✅ Windows: Puede acceder al portal vía navegador
- [ ] ✅ Teléfono: Puede acceder al portal vía navegador

---

## 🚀 COMANDOS RÁPIDOS DE REFERENCIA

### En Windows (PowerShell)

```powershell
# Ver configuración de red
ipconfig /all

# Ver adaptadores activos
Get-NetAdapter | Where-Object {$_.Status -eq "Up"}

# Hacer ping a la VM
ping 192.168.43.100

# Verificar conectividad de puerto
Test-NetConnection -ComputerName 192.168.43.100 -Port 80
```

### En VM Linux

```bash
# Ver IP y configuración de red
ip addr show
ip route show

# Verificar conectividad
ping -c 4 192.168.43.1  # Ping al gateway (teléfono)
ping -c 4 8.8.8.8       # Ping a internet

# Verificar puertos abiertos
sudo netstat -tuln | grep -E ':(80|443|53)'

# Ver procesos del portal
ps aux | grep -E '(server.py|dns_server.py)'

# Iniciar el portal
sudo ./scripts/start_captive_portal.sh

# Detener el portal
sudo ./scripts/stop_captive_portal.sh

# Ver logs en tiempo real (si usas systemd)
sudo journalctl -u captive-portal -f
```

---

## 💡 CONSEJOS ADICIONALES

### 1. Modo Avión en el Teléfono

Para forzar que el teléfono use solo la red del hotspot:

- Activa **modo avión**
- Luego activa **WiFi** manualmente
- Conéctate a tu propio hotspot (sí, es posible en algunos Android con hotspot WiFi extendido)

### 2. Usar IP Reservada en el Hotspot

Algunos teléfonos permiten reservar IPs para dispositivos específicos:

- Ve a configuración del hotspot
- Busca "Dispositivos conectados" o "Clientes"
- Reserva la IP `192.168.43.100` para la MAC de tu VM

### 3. Debugging Avanzado

Captura tráfico de red en la VM:

```bash
# Instalar tcpdump
sudo apt-get install tcpdump

# Capturar tráfico HTTP
sudo tcpdump -i enp0s3 -n port 80

# Capturar tráfico DNS
sudo tcpdump -i enp0s3 -n port 53
```

### 4. Acceso Remoto SSH

Para configurar la VM más fácilmente desde Windows:

```bash
# En la VM, instalar y habilitar SSH
sudo apt-get install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

Desde Windows (PowerShell):

```powershell
ssh usuario@192.168.43.100
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- [01-DETECCION-AUTOMATICA.md](./01-DETECCION-AUTOMATICA.md) - Cómo funciona la detección automática del portal
- [02-HTTPS-SSL.md](./02-HTTPS-SSL.md) - Configuración de certificados SSL
- [03-ANTI-SUPLANTACION.md](./03-ANTI-SUPLANTACION.md) - Seguridad y verificación MAC
- [04-NAT-MASQUERADING.md](./04-NAT-MASQUERADING.md) - Configuración NAT
- [README.md](../README.md) - Documentación principal del proyecto

---

## ❓ PREGUNTAS FRECUENTES

### ¿Puedo usar una IP diferente para la VM?

Sí, pero debe estar en el mismo rango de red que el hotspot. Por ejemplo:

- Si el hotspot usa `192.168.43.0/24`, elige cualquier IP entre `192.168.43.2` y `192.168.43.254`
- Evita usar `.1` (gateway) y las IPs ya asignadas a otros dispositivos

### ¿Qué pasa si cambio de hotspot o red?

Necesitarás:

1. Reconfigurar la IP estática de la VM con el nuevo rango de red
2. Actualizar el gateway en la configuración de red
3. Reiniciar el portal

### ¿Puedo usar WiFi compartido desde el PC en lugar del teléfono?

Sí, el proceso es similar. Windows puede crear un hotspot móvil:

1. **Configuración** → **Red e Internet** → **Zona con cobertura inalámbrica móvil**
2. Activa "Compartir mi conexión a Internet"

### ¿Funciona con VirtualBox en modo NAT?

No es recomendado para este escenario. El modo NAT hace que la VM esté en una red privada diferente, necesitarías port forwarding complejo. Usa **Bridged** como se explica aquí.

---

**¡Listo! Ahora tienes todo configurado para probar tu portal cautivo desde tu teléfono y PC Windows.** 🎉

Si encuentras algún problema, revisa la sección de **SOLUCIÓN DE PROBLEMAS** o verifica el checklist completo.

1. **Aceptar el riesgo**: En el navegador, cuando aparezca la advertencia:
   - Chrome: Click en "Avanzado" → "Continuar a [IP] (no seguro)"
   - Firefox: "Avanzado" → "Aceptar el riesgo y continuar"

2. **Usar HTTP en lugar de HTTPS** (solo para pruebas):
   - Navega a `http://IP` en vez de `https://IP`

3. **Generar certificado válido para la IP**:
   ```bash
   # En la VM
   openssl req -x509 -newkey rsa:4096 -nodes \
     -keyout key.pem -out cert.pem -days 365 \
     -subj "/CN=192.168.43.100"
   ```

### Problema: "Connection refused" o "No se puede acceder"

1. **Verificar que el servidor esté corriendo**:
   ```bash
   sudo systemctl status NetworkManager  # Si usas NetworkManager
   ps aux | grep python3
   ```

2. **Verificar logs**:
   ```bash
   sudo journalctl -u captive-portal -f  # Si creaste un servicio
   # O ver los logs del script directamente
   ```

3. **Reiniciar el portal**:
   ```bash
   cd scripts
   sudo ./stop_captive_portal.sh
   sudo ./start_captive_portal.sh
   ```

### Problema: La VM no obtiene IP en modo Bridged

1. **Verificar DHCP**:
   ```bash
   sudo dhclient -r  # Liberar IP
   sudo dhclient     # Obtener nueva IP
   ```

2. **Configuración manual si es necesario**:
   ```bash
   sudo ip addr add 192.168.43.100/24 dev eth0
   sudo ip route add default via 192.168.43.1
   ```

---

## 7. Comandos Útiles de Diagnóstico

### En Windows:

```powershell
# Ver todas las conexiones de red
ipconfig /all

# Ver tabla ARP (dispositivos en la red)
arp -a

# Ver reglas de firewall
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Captive*"}

# Ver port forwarding activo
netsh interface portproxy show all

# Escanear puerto
Test-NetConnection -ComputerName IP -Port 80
```

### En Linux (VM):

```bash
# Ver interfaces y IPs
ip addr show
ip route show

# Ver puertos escuchando
sudo netstat -tulpn
sudo ss -tlnp

# Ver procesos Python
ps aux | grep python

# Ver logs del sistema
sudo journalctl -xe

# Verificar conectividad
ping 8.8.8.8  # Internet
ping 192.168.43.1  # Gateway
```

### En el Teléfono:

- **Apps recomendadas**:
  - Fing (Android/iOS): Escaneo de red
  - Network Analyzer (iOS): Diagnóstico de red
  - PingTools (Android): Herramientas de red

---

## 8. Resumen de IPs y Puertos

### Tabla de Referencia:

| Dispositivo | Interfaz | IP Ejemplo | Propósito |
|-------------|----------|------------|-----------|
| Teléfono | WiFi Hotspot | 192.168.43.1 | Gateway/Router |
| PC Windows | WiFi | 192.168.43.5 | Cliente |
| PC Windows | VBox Host-Only | 192.168.56.1 | Comunicación con VM |
| VM Linux | eth0 (Bridged) | 192.168.43.100 | Portal Cautivo |
| VM Linux | eth1 (Host-Only) | 192.168.56.101 | Comunicación con Windows |

### Puertos Utilizados:

| Puerto | Protocolo | Servicio |
|--------|-----------|----------|
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |
| 53 | UDP | DNS |

---

## 9. Checklist de Configuración

### Antes de Probar:

- [ ] VirtualBox configurado con adaptador Bridged
- [ ] VM iniciada y con IP asignada
- [ ] Firewall de Windows configurado (reglas creadas)
- [ ] Firewall de Linux configurado (puertos abiertos)
- [ ] Portal cautivo corriendo (`sudo python3 server.py`)
- [ ] Servidor escuchando en `0.0.0.0:80` (verificado con `netstat`)

### Para Probar desde Windows:

- [ ] Ping exitoso a la IP de la VM
- [ ] Puerto 80 accesible (Test-NetConnection)
- [ ] Navegador puede cargar `http://IP_VM`

### Para Probar desde Teléfono:

- [ ] Conectado al mismo hotspot WiFi
- [ ] IP de la VM anotada
- [ ] Navegador puede cargar `http://IP_VM`

---

## 10. Recomendaciones

### Para Pruebas:

1. **Usa el Modo A (Bridged)**: Es más simple y realista
2. **Desactiva HTTPS temporalmente**: Evita problemas con certificados
3. **Usa IPs fijas en la VM**: Facilita las pruebas

### Configurar IP Estática en la VM:

Edita `/etc/netplan/01-netcfg.yaml` (Ubuntu/Debian):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.43.100/24
      gateway4: 192.168.43.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Aplica cambios:
```bash
sudo netplan apply
```

### Para Producción:

1. Genera certificados SSL válidos
2. Configura DNS apropiadamente
3. Implementa las reglas de NAT/iptables
4. Configura el servicio systemd para inicio automático

---

## 11. Próximos Pasos

Una vez que el portal funcione en este escenario de prueba, puedes:

1. **Implementar detección automática del portal** (ver `01-DETECCION-AUTOMATICA.md`)
2. **Configurar HTTPS correctamente** (ver `02-HTTPS-SSL.md`)
3. **Agregar NAT/Masquerading** (ver `04-NAT-MASQUERADING.md`)
4. **Mejorar el diseño UX** (ver `05-DISENO-UX.md`)

---

**Última actualización**: 5 de diciembre de 2025
