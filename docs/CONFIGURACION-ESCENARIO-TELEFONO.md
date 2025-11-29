# 📱 Configuración Portal Cautivo: Teléfono + Laptop + VM

## 🎯 Tu Escenario

```
📱 Teléfono (Hotspot WiFi) → Proporciona Internet
    ↓
🌐 Red WiFi (192.168.43.x)
    ↓
    ├─ 💻 Laptop Windows (192.168.43.X) → Dispositivo de prueba 1
    └─ 🖥️ VM Ubuntu en VirtualBox (192.168.43.100) → Portal Cautivo
```

**Dispositivos de prueba**: Teléfono y Laptop Windows
**Objetivo**: Bloquear internet hasta que se autentiquen en el portal

---

## ⚠️ LIMITACIÓN IMPORTANTE

**EL PROYECTO ACTUAL NO FUNCIONARÁ EN TU ESCENARIO** porque:

1. Tu VM tiene **solo 1 interfaz** (modo bridge al WiFi del teléfono)
2. El proyecto espera **2 interfaces** (LAN para clientes, WAN para internet)
3. Tu teléfono ya es el **gateway/router**, no la VM

## ✅ SOLUCIONES DISPONIBLES

### **Solución 1: Modo Demostración Simple** ⭐ RECOMENDADO PARA EMPEZAR

En este modo:
- La VM corre el servidor web del portal
- Los dispositivos acceden **manualmente** a `http://192.168.43.100`
- El login es funcional pero **NO bloquea automáticamente** el internet
- Es útil para probar la interfaz web y el flujo de autenticación

**Ventajas**: Simple, rápido de configurar
**Desventajas**: No es un portal cautivo "real" (no redirige tráfico automáticamente)

---

### **Solución 2: VM con Doble Interfaz** ⭐ PORTAL CAUTIVO COMPLETO

En este modo:
- La VM tiene **2 interfaces de red**
- Los dispositivos se conectan a través de la VM
- La VM bloquea y redirige todo el tráfico
- **Funciona como un portal cautivo real**

**Ventajas**: Portal cautivo completo y funcional
**Desventajas**: Configuración más compleja

---

## 🚀 SOLUCIÓN 1: Modo Demostración (Configuración Rápida)

### Paso 1: Configurar el Hotspot del Teléfono

1. **Activa el hotspot WiFi** en tu teléfono
2. **Anota estos datos**:
   - Nombre de la red WiFi
   - Contraseña
   - IP del teléfono (generalmente `192.168.43.1`)

### Paso 2: Conectar Windows al Hotspot

1. Conecta tu laptop Windows al hotspot del teléfono
2. Abre **PowerShell** y ejecuta:

```powershell
ipconfig
```

3. **Anota**:
   - IP de Windows: `_______________` (ej: 192.168.43.5)
   - Gateway: `_______________` (ej: 192.168.43.1)

### Paso 3: Configurar VirtualBox (Modo Bridge)

1. **Apaga la VM** si está encendida
2. En VirtualBox, selecciona tu VM → **Configuración**
3. Ve a **Red** → **Adaptador 1**:
   - ☑️ Habilitar adaptador de red
   - **Conectado a**: Adaptador puente (Bridged Adapter)
   - **Nombre**: Selecciona tu adaptador WiFi de Windows
   - **Modo promiscuo**: Permitir todo
4. **Guarda** y arranca la VM

### Paso 4: Configurar IP Estática en la VM

1. Dentro de la VM Ubuntu, abre terminal
2. Identifica tu interfaz de red:

```bash
ip addr show
```

3. Configura IP estática (usa **Netplan** en Ubuntu 18.04+):

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

4. Contenido (ajusta según tu red):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:  # ← Tu interfaz (puede ser eth0, ens33, etc.)
      dhcp4: no
      addresses:
        - 192.168.43.100/24  # ← IP fija para la VM
      routes:
        - to: default
          via: 192.168.43.1  # ← IP del teléfono
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

5. Aplica cambios:

```bash
sudo netplan apply
```

6. Verifica:

```bash
ip addr show
ping 8.8.8.8  # Debe funcionar
```

### Paso 5: Preparar el Proyecto (Modo Demo)

1. En la VM, navega al proyecto:

```bash
cd ~/captive-portal  # O donde esté tu proyecto
```

2. Crea un script simplificado para modo demo:

```bash
nano demo_server.sh
```

3. Contenido del script:

```bash
#!/bin/bash
# Script para ejecutar el portal en modo demostración

echo "========================================="
echo "   PORTAL CAUTIVO - Modo Demostración"
echo "========================================="
echo ""

# Obtener la IP de la VM
VM_IP=$(hostname -I | awk '{print $1}')

echo "🌐 Servidor del portal iniciando en: http://$VM_IP:80"
echo ""
echo "📱 Para probar desde tus dispositivos:"
echo "   1. Conecta el teléfono y la laptop al hotspot"
echo "   2. Abre el navegador en: http://$VM_IP"
echo "   3. Usa las credenciales de users.json"
echo ""
echo "⚠️  NOTA: Este modo es solo demostración."
echo "   No bloquea el internet automáticamente."
echo ""
echo "Presiona Ctrl+C para detener el servidor."
echo ""

# Ejecutar el servidor sin scripts de iptables
sudo python3 server.py
```

4. Dar permisos:

```bash
chmod +x demo_server.sh
```

5. Ejecutar:

```bash
sudo ./demo_server.sh
```

### Paso 6: Verificar Usuarios

Revisa que tengas usuarios en `users.json`:

```bash
cat users.json
```

Debe verse algo como:

```json
{
  "admin": "admin123",
  "user1": "password1"
}
```

### Paso 7: Probar desde los Dispositivos

#### Desde la Laptop Windows:

1. Abre el navegador
2. Ve a: `http://192.168.43.100`
3. Deberías ver el formulario de login
4. Ingresa usuario y contraseña
5. Si es correcto, verás la página de éxito

#### Desde el Teléfono:

1. Abre el navegador (Chrome, Safari, etc.)
2. Ve a: `http://192.168.43.100`
3. Prueba el login

### ✅ ¿Qué funciona en este modo?

- ✅ Servidor web funcionando
- ✅ Formulario de login
- ✅ Autenticación de usuarios
- ✅ Redirección después del login
- ❌ **NO** bloquea internet automáticamente
- ❌ **NO** redirige tráfico HTTP/HTTPS al portal

---

## 🔥 SOLUCIÓN 2: Portal Cautivo Completo (Doble Interfaz)

### Arquitectura de Red

```
📱 Teléfono (Hotspot)
    ↓ WiFi
💻 Laptop Windows ────┐
    VirtualBox        │
    ┌─────────────────┴────────┐
    │ VM Ubuntu (Portal)       │
    │                          │
    │ [enp0s3] Bridge          │ → Internet desde teléfono
    │ 192.168.43.100           │
    │                          │
    │ [enp0s8] Red Interna     │ → Red para clientes
    │ 10.0.0.1                 │
    └──────────────────────────┘
         ↓
    Clientes conectan aquí
```

### Paso 1: Configurar 2 Adaptadores en VirtualBox

1. **Apaga la VM**
2. En VirtualBox → Configuración → **Red**

#### Adaptador 1 (Conexión a Internet):
- ☑️ Habilitar adaptador de red
- **Conectado a**: Adaptador puente
- **Nombre**: Tu adaptador WiFi
- **Modo promiscuo**: Permitir todo

#### Adaptador 2 (Red para Clientes):
- ☑️ Habilitar adaptador de red
- **Conectado a**: Red interna
- **Nombre**: intnet
- **Modo promiscuo**: Permitir todo

3. **Guarda** y arranca la VM

### Paso 2: Configurar las Interfaces en la VM

1. Identifica las interfaces:

```bash
ip addr show
```

Verás algo como:
- `enp0s3`: Bridge (para internet)
- `enp0s8`: Red interna (para clientes)

2. Configura `/etc/netplan/01-netcfg.yaml`:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:  # WAN - Conexión a internet
      dhcp4: no
      addresses:
        - 192.168.43.100/24
      routes:
        - to: default
          via: 192.168.43.1  # Gateway del teléfono
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
    
    enp0s8:  # LAN - Red para clientes
      dhcp4: no
      addresses:
        - 10.0.0.1/24  # IP del portal en la red interna
```

3. Aplica:

```bash
sudo netplan apply
```

4. Habilita IP forwarding:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

### Paso 3: Configurar DHCP en la VM (para clientes)

1. Instala dnsmasq:

```bash
sudo apt update
sudo apt install -y dnsmasq
```

2. Configura `/etc/dnsmasq.conf`:

```bash
sudo nano /etc/dnsmasq.conf
```

3. Agrega al final:

```conf
interface=enp0s8
dhcp-range=10.0.0.10,10.0.0.50,12h
dhcp-option=3,10.0.0.1  # Gateway
dhcp-option=6,10.0.0.1  # DNS
```

4. Reinicia dnsmasq:

```bash
sudo systemctl restart dnsmasq
sudo systemctl enable dnsmasq
```

### Paso 4: Actualizar Scripts del Proyecto

Edita `scripts/detect_interfaces.sh` para asegurar que detecte correctamente:

```bash
# Debe detectar:
# WAN_IF=enp0s3 (bridge a internet)
# LAN_IF=enp0s8 (red interna)
```

### Paso 5: Ejecutar el Portal Cautivo

```bash
cd ~/captive-portal
sudo ./scripts/start_captive_portal.sh
```

### Paso 6: Conectar Dispositivos a la VM

#### En Windows:

1. Ve a **Configuración** → **Red e Internet** → **WiFi**
2. Cambia las propiedades del adaptador WiFi
3. Configura IP manual:
   - IP: `10.0.0.10`
   - Máscara: `255.255.255.0`
   - Gateway: `10.0.0.1` (la VM)
   - DNS: `10.0.0.1`

#### En el Teléfono:

1. **Problema**: No puedes conectar el teléfono a la red interna de la VM si el teléfono es el que proporciona internet

**Solución**: Usa otro dispositivo o una segunda red WiFi

---

## 📊 Comparación de Soluciones

| Característica | Solución 1 (Demo) | Solución 2 (Completo) |
|----------------|-------------------|------------------------|
| Complejidad | ⭐ Fácil | ⭐⭐⭐ Difícil |
| Tiempo de setup | 15 min | 1-2 horas |
| Bloqueo automático | ❌ No | ✅ Sí |
| Redirección HTTP/HTTPS | ❌ No | ✅ Sí |
| Portal cautivo real | ❌ No | ✅ Sí |
| Prueba con teléfono | ✅ Sí | ⚠️ Limitado |

---

## 🎯 RECOMENDACIÓN FINAL

**Para tu escenario específico (teléfono como fuente de internet):**

1. **Empieza con la Solución 1 (Modo Demo)**
   - Podrás probar la interfaz web
   - Verificar el login funciona
   - Es rápido de configurar

2. **Para un portal cautivo real**, considera:
   - **Opción A**: Usar un router físico en lugar del teléfono
   - **Opción B**: Configurar la VM con 2 interfaces pero usar la laptop Windows como punto de acceso WiFi adicional
   - **Opción C**: Usar una Raspberry Pi como gateway intermedio

---

## 🛠️ Solución Alternativa: Windows como Gateway

Si quieres el bloqueo automático sin complicar la VM:

1. Configura la laptop Windows para compartir internet
2. Los dispositivos se conectan a la laptop
3. La VM corre el portal
4. La laptop hace NAT y redirige al portal

¿Te gustaría que desarrolle esta opción?

---

## 📝 Credenciales de Prueba

Por defecto en `users.json`:
```json
{
  "admin": "admin123",
  "user1": "password1"
}
```

---

## ❓ Preguntas Frecuentes

### ¿Por qué no funciona el bloqueo automático en Solución 1?

Porque tu VM está en la **misma red** que los clientes (modo bridge). Para bloquear tráfico, la VM debe ser el **gateway** entre los clientes e internet, lo que requiere 2 interfaces de red.

### ¿Puedo usar el teléfono como dispositivo de prueba en Solución 2?

Es complicado porque el teléfono es la fuente de internet. Necesitarías otro dispositivo o una segunda red WiFi.

### ¿Funciona en una red empresarial o doméstica?

Sí, el portal funciona mejor en redes donde puedes controlar el gateway. En tu casa con un router normal, la Solución 2 funciona perfectamente.

---

## 🚨 Próximos Pasos

Dime cuál solución prefieres y te ayudo a configurarla paso a paso:

1. **Solución 1 (Demo)**: Rápida, para probar la interfaz
2. **Solución 2 (Completo)**: Portal real con 2 interfaces
3. **Opción Alternativa**: Windows como gateway

¿Cuál quieres implementar?
