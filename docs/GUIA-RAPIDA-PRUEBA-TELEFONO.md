# 🚀 Guía Rápida: Prueba con Teléfono + Laptop + VM

## ⏱️ Configuración Rápida (15 minutos)

Esta guía te permite probar el portal cautivo en **modo demostración** usando tu teléfono como hotspot.

---

## 📱 PASO 1: Configurar Teléfono (2 min)

1. **Activa el hotspot WiFi** en tu teléfono
2. **Anota**:
   - Nombre de red: `________________`
   - Contraseña: `________________`

---

## 💻 PASO 2: Conectar Laptop Windows (2 min)

1. Conecta tu laptop al hotspot del teléfono
2. Abre **PowerShell** y ejecuta:

```powershell
ipconfig
```

3. **Busca el adaptador WiFi** y anota:
   - IP de Windows: `________________` (ej: 192.168.43.5)
   - Gateway: `________________` (ej: 192.168.43.1)

---

## 🖥️ PASO 3: Configurar VirtualBox (3 min)

1. **Apaga la VM** si está encendida
2. En VirtualBox → Configuración → **Red**
3. **Adaptador 1**:
   - ☑️ Habilitar adaptador de red
   - **Conectado a**: Adaptador puente (Bridged)
   - **Nombre**: Tu adaptador WiFi (busca el nombre que tiene WiFi/Wireless)
   - **Modo promiscuo**: Permitir todo
4. **Guarda** y arranca la VM

---

## 🐧 PASO 4: Configurar IP en la VM (5 min)

### 4.1 Identificar la interfaz

```bash
ip addr show
```

Busca tu interfaz (puede ser `eth0`, `enp0s3`, `ens33`, etc.)

### 4.2 Configurar IP estática

**Para Ubuntu 18.04+ (Netplan):**

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

Contenido (ajusta `enp0s3` y las IPs según tu red):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:  # ← CAMBIAR por tu interfaz
      dhcp4: no
      addresses:
        - 192.168.43.100/24  # ← IP fija para la VM
      routes:
        - to: default
          via: 192.168.43.1  # ← Gateway (IP del teléfono)
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Aplicar:

```bash
sudo netplan apply
```

**Para Ubuntu/Debian antiguo:**

```bash
sudo nano /etc/network/interfaces
```

```
auto eth0
iface eth0 inet static
    address 192.168.43.100
    netmask 255.255.255.0
    gateway 192.168.43.1
    dns-nameservers 8.8.8.8
```

```bash
sudo systemctl restart networking
```

### 4.3 Verificar conectividad

```bash
ping -c 4 8.8.8.8
```

Debe funcionar ✅

---

## 🎯 PASO 5: Ejecutar el Portal (3 min)

### 5.1 Verificar configuración

```bash
cd ~/captive-portal  # O donde esté tu proyecto
sudo ./scripts/check_network.sh
```

Esto te mostrará si todo está OK ✅

### 5.2 Ejecutar en modo demostración

```bash
sudo ./scripts/demo_mode.sh
```

Deberías ver:

```
🚀 Iniciando servidor del portal...
   Puerto: 80
   URL: http://192.168.43.100

✅ Servidor iniciado correctamente
```

**¡Deja este terminal abierto!** El servidor está corriendo.

---

## 🧪 PASO 6: Probar desde los Dispositivos

### Desde la Laptop Windows:

1. Abre tu navegador favorito
2. Ve a: `http://192.168.43.100`
3. Deberías ver el formulario de login
4. Ingresa:
   - Usuario: `admin`
   - Contraseña: `admin123`
5. Si es correcto → Página de éxito ✅

### Desde el Teléfono:

1. Abre Chrome/Safari
2. Ve a: `http://192.168.43.100`
3. Prueba el login igual que arriba

---

## 👥 Usuarios de Prueba

Por defecto en `users.json`:

```json
{
  "admin": "admin123",
  "user1": "password1",
  "demo": "demo123"
}
```

Puedes agregar más editando el archivo.

---

## ⚠️ Limitaciones del Modo Demo

Este modo **NO** es un portal cautivo completo:

- ❌ **NO** bloquea internet automáticamente
- ❌ **NO** redirige tráfico HTTP/HTTPS al portal
- ❌ Los usuarios pueden seguir navegando sin autenticarse
- ✅ **SÍ** funciona el login y la autenticación
- ✅ **SÍ** puedes ver y probar la interfaz web

Es útil para:
- ✅ Probar que el servidor funciona
- ✅ Verificar la interfaz web
- ✅ Comprobar la autenticación de usuarios
- ✅ Entender cómo funciona el flujo

---

## 🔥 ¿Quieres un Portal Cautivo Completo?

Para tener **bloqueo automático** y **redirección de tráfico**, consulta:

```
docs/CONFIGURACION-ESCENARIO-TELEFONO.md
```

Ahí encontrarás la configuración con **2 interfaces de red**.

---

## 🐛 Solución de Problemas

### ❌ No puedo acceder a `http://192.168.43.100`

**Verifica:**

1. ¿La VM tiene IP `192.168.43.100`?
   ```bash
   ip addr show
   ```

2. ¿El servidor está corriendo?
   ```bash
   sudo netstat -tuln | grep :80
   ```
   Debería mostrar algo en el puerto 80

3. ¿Hay conectividad entre dispositivos?
   ```bash
   # Desde la VM, hacer ping a la laptop Windows
   ping 192.168.43.5  # (tu IP de Windows)
   ```

### ❌ Error "Address already in use"

El puerto 80 ya está ocupado. Verifica qué proceso lo usa:

```bash
sudo netstat -tuln | grep :80
sudo lsof -i :80
```

Para liberar el puerto:

```bash
# Si es Apache
sudo systemctl stop apache2

# Si es Nginx
sudo systemctl stop nginx
```

### ❌ Permission denied al ejecutar scripts

Los scripts necesitan permisos de ejecución:

```bash
cd ~/captive-portal
chmod +x scripts/*.sh
```

### ❌ No hay internet en la VM

Verifica:

1. ¿El gateway está bien configurado?
   ```bash
   ip route show
   ```
   Debe mostrar: `default via 192.168.43.1 ...`

2. ¿DNS funciona?
   ```bash
   nslookup google.com
   ```

3. ¿Firewall bloqueando?
   ```bash
   sudo ufw status
   # Si está activo:
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

---

## 📊 Arquitectura de lo que Estás Probando

```
┌──────────────┐
│   Teléfono   │  📱 Hotspot (192.168.43.1)
└──────┬───────┘
       │
       │ WiFi
       │
       ├─────────────────────────────────────┐
       │                                     │
┌──────▼──────┐                    ┌────────▼────────┐
│   Laptop    │                    │   VM Ubuntu     │
│   Windows   │                    │  Portal Cautivo │
│ 192.168.43.5│                    │ 192.168.43.100  │
└─────────────┘                    └─────────────────┘
       │                                     │
       └─── Abre navegador en: ─────────────┘
            http://192.168.43.100
```

**Flujo:**
1. Usuario abre navegador → `http://192.168.43.100`
2. Servidor en VM muestra formulario de login
3. Usuario ingresa credenciales
4. Si son correctas → Página de éxito
5. En modo demo, el internet **NO** se bloquea automáticamente

---

## ✅ Checklist Final

Antes de probar, verifica:

- [ ] Teléfono con hotspot activo
- [ ] Laptop Windows conectada al hotspot
- [ ] VM con modo bridge configurado
- [ ] VM con IP estática (192.168.43.100)
- [ ] VM puede hacer ping a 8.8.8.8
- [ ] Servidor corriendo en la VM (puerto 80)
- [ ] Navegador en laptop puede abrir `http://192.168.43.100`

---

## 📞 Siguiente Paso

Si todo funciona en modo demo, puedes:

1. **Personalizar la interfaz**: Edita `templates/index.html`
2. **Agregar usuarios**: Edita `users.json`
3. **Configurar portal completo**: Ver `docs/CONFIGURACION-ESCENARIO-TELEFONO.md`

---

## 🎉 ¡Éxito!

Si llegaste hasta aquí y funciona, ¡felicitaciones! 🎊

Tienes un servidor web funcionando que simula un portal cautivo. Aunque no bloquea internet automáticamente, es un buen punto de partida para entender cómo funcionan estos sistemas.
