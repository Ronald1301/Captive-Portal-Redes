# 🚀 Guía Rápida - Probar Portal con Teléfono + Windows + VM

**Escenario**: Teléfono (Hotspot) → PC Windows → VM Linux (Portal)

---

## 📋 Resumen de Pasos

### 1️⃣ Preparar Teléfono (2 min)

```
✅ Activar hotspot WiFi
✅ Anotar IP del hotspot (generalmente 192.168.43.1)
```

### 2️⃣ Conectar Windows (2 min)

```powershell
# Conectar al hotspot del teléfono
# Ejecutar en PowerShell:
ipconfig /all

# Anotar:
# - IP de Windows: ej. 192.168.43.5
# - Gateway: ej. 192.168.43.1
# - Nombre del adaptador WiFi
```

### 3️⃣ Configurar VirtualBox (3 min)

```
1. VM → Configuración → Red
2. Adaptador 1:
   ✅ Habilitar
   ✅ Adaptador puente (Bridged)
   ✅ Nombre: Tu adaptador WiFi de Windows
   ✅ Modo promiscuo: Permitir todo
3. Guardar
```

### 4️⃣ Configurar VM Linux (10 min)

```bash
# 1. Ver interfaz de red
ip addr show

# 2. Configurar IP estática (Ejemplo Ubuntu con Netplan)
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:  # ← Tu interfaz
      dhcp4: no
      addresses:
        - 192.168.43.100/24  # ← IP fija
      gateway4: 192.168.43.1  # ← IP del teléfono
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
# 3. Aplicar configuración
sudo netplan apply

# 4. Verificar
ip addr show
ping -c 4 192.168.43.1  # Ping al teléfono
ping -c 4 8.8.8.8       # Ping a internet
```

### 5️⃣ Configurar Firewall Windows (5 min)

```powershell
# Abrir PowerShell como Administrador

# Permitir puertos
New-NetFirewallRule -DisplayName "Captive Portal HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Captive Portal HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "Captive Portal DNS" -Direction Inbound -Protocol UDP -LocalPort 53 -Action Allow
```

### 6️⃣ Configurar Portal (5 min)

```bash
cd ~/captive-portal  # Tu ruta

# 1. Configurar interfaz
nano scripts/start_captive_portal.sh
# Cambiar: LAN_IF="enp0s3"  # Tu interfaz

# 2. Crear usuario
python3 auth.py add testuser password123

# 3. Generar certificados (opcional)
./generate_cert.sh
# Common Name: 192.168.43.100

# 4. Dar permisos
chmod +x scripts/*.sh
```

### 7️⃣ Iniciar Portal (1 min)

```bash
sudo ./scripts/start_captive_portal.sh
```

Deberías ver:

```text
🚀 Iniciando Portal Cautivo...
✅ Servidor HTTP iniciado en puerto 80
✅ Servidor HTTPS iniciado en puerto 443
✅ DNS server iniciado en puerto 53
🌐 Portal disponible en: http://192.168.43.100
```

### 8️⃣ Probar (2 min)

**Desde Windows**:

1. Abrir navegador
2. Ir a: `http://192.168.43.100`
3. Login: `testuser` / `password123`

**Desde Teléfono**:

1. Desactivar datos móviles
2. Abrir navegador
3. Ir a: `http://192.168.43.100`
4. Login: `testuser` / `password123`

---

## 📊 Tabla de IPs

| Dispositivo | IP | Uso |
|-------------|-----|-----|
| **Teléfono** | `192.168.43.1` | Gateway |
| **PC Windows** | `192.168.43.5` | Cliente |
| **VM Linux** | `192.168.43.100` | Portal |

---

## 🐛 Problemas Comunes

### ❌ No puedo acceder al portal

```bash
# En VM: Verificar que el servidor esté corriendo
sudo netstat -tuln | grep -E ':(80|443|53)'

# Debería mostrar:
# tcp  0.0.0.0:80   LISTEN
# tcp  0.0.0.0:443  LISTEN
# udp  0.0.0.0:53
```

```powershell
# En Windows: Verificar conectividad
ping 192.168.43.100
Test-NetConnection -ComputerName 192.168.43.100 -Port 80
```

### ❌ La VM no tiene internet

```bash
# Verificar gateway
ip route show
# Debe mostrar: default via 192.168.43.1

# Hacer ping
ping -c 4 192.168.43.1  # Al teléfono
ping -c 4 8.8.8.8       # A internet
```

### ❌ Firewall bloqueando

```bash
# En Linux: Desactivar temporalmente para probar
sudo ufw disable

# Luego abrir puertos correctamente
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 53/udp
sudo ufw enable
```

```powershell
# En Windows: Verificar reglas
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Captive*"}
```

---

## ✅ Checklist

- [ ] Teléfono: Hotspot activado
- [ ] Windows: Conectado al hotspot
- [ ] Windows: IP anotada (ej: 192.168.43.5)
- [ ] VirtualBox: Modo Bridged configurado
- [ ] VM: IP estática (ej: 192.168.43.100)
- [ ] VM: Puede hacer ping al teléfono
- [ ] VM: Tiene internet
- [ ] Firewall Windows: Reglas creadas
- [ ] Portal: Interfaz configurada
- [ ] Portal: Usuario creado
- [ ] Portal: Servidor corriendo
- [ ] Windows: Puede hacer ping a VM
- [ ] Windows: Puede acceder al portal
- [ ] Teléfono: Puede acceder al portal

---

## 🔍 Comandos de Verificación

### Ver IP de Windows

```powershell
ipconfig /all
```

### Ver IP de VM

```bash
ip addr show
```

### Verificar puertos abiertos en VM

```bash
sudo netstat -tuln | grep -E ':(80|443|53)'
```

### Ping desde Windows a VM

```powershell
ping 192.168.43.100
```

### Ver logs del portal en VM

```bash
# Si corre en terminal, verás los logs ahí
# Si usas systemd:
sudo journalctl -u captive-portal -f
```

---

## 📚 Documentación Completa

Para detalles completos, ver: [06-CONFIGURACION-PRUEBAS-VIRTUALBOX.md](./06-CONFIGURACION-PRUEBAS-VIRTUALBOX.md)

---

**Tiempo total estimado**: ~30 minutos

**Última actualización**: 5 de diciembre de 2025
