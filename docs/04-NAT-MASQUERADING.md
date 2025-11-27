# Enmascaramiento IP (NAT)

**Requisito Extra:** 0.25 puntos  
**Estado:** ✅ Implementado

## 🌐 Descripción

Servicio de traducción de direcciones de red (NAT) que enmascara las IPs privadas de los clientes con la IP pública del gateway, permitiendo que múltiples dispositivos compartan una única conexión a internet.

## 🔧 ¿Qué es NAT/MASQUERADE?

**NAT (Network Address Translation)** traduce direcciones IP privadas a públicas y viceversa.

**MASQUERADE** es un tipo específico de NAT que:
- Enmascara múltiples IPs privadas con una sola IP pública
- Se usa cuando la IP pública es dinámica (DHCP en WAN)
- Es la función CORE de cualquier router doméstico

## 📊 Funcionamiento

### Sin NAT:
```
Cliente: 192.168.1.10 → Internet
❌ Error: IP privada no es ruteable en internet
```

### Con NAT:
```
Cliente: 192.168.1.10:45678 → Google: 8.8.8.8:53
    ↓ Gateway aplica MASQUERADE
Gateway: 200.1.2.3:12345 → Google: 8.8.8.8:53
    ↓ Google responde
Google: 8.8.8.8:53 → Gateway: 200.1.2.3:12345
    ↓ Gateway traduce de vuelta
Cliente: 192.168.1.10:45678 ← Gateway
✅ Éxito: Cliente recibe respuesta
```

## 💻 Implementación

### Archivo: `scripts/nat_setup.sh`

```bash
#!/bin/bash
# Detectar interfaz WAN
source detect_interfaces.sh

# Configurar NAT MASQUERADE
iptables -t nat -A POSTROUTING -o $WAN_IF -j MASQUERADE

echo "NAT configurado en $WAN_IF"
```

### Regla iptables

```bash
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

**Explicación:**
- `-t nat`: Usa la tabla NAT
- `-A POSTROUTING`: Agrega regla a la cadena POSTROUTING (después de ruteo)
- `-o eth0`: Solo para paquetes que salen por interfaz WAN
- `-j MASQUERADE`: Acción: enmascarar con la IP de la interfaz de salida

## 🎯 Por Qué es Necesario

### Rango de IPs Privadas (No ruteables en internet):
- `10.0.0.0/8` (10.0.0.0 - 10.255.255.255)
- `172.16.0.0/12` (172.16.0.0 - 172.31.255.255)
- `192.168.0.0/16` (192.168.0.0 - 192.168.255.255)

**Sin NAT:** Los routers de internet descartarían paquetes con estas IPs origen.

**Con NAT:** El gateway traduce a su IP pública antes de enviar.

## 🔍 Tabla de Traducción

El kernel mantiene una tabla de conexiones:

```
IP Privada      Puerto  →  IP Pública     Puerto  →  Destino
192.168.1.10    45678   →  200.1.2.3      12345   →  8.8.8.8:53
192.168.1.15    56789   →  200.1.2.3      12346   →  1.1.1.1:443
192.168.1.20    12340   →  200.1.2.3      12347   →  142.250.185.78:80
```

Cuando llega una respuesta a `200.1.2.3:12345`, el gateway sabe que debe enviarla a `192.168.1.10:45678`.

## 🧪 Verificación

### Ver reglas NAT activas
```bash
sudo iptables -t nat -L -v -n

# Salida esperada:
Chain POSTROUTING (policy ACCEPT 0 packets, 0 bytes)
pkts bytes target     prot opt in     out     source        destination
 123  45K MASQUERADE all  --  *      eth0    0.0.0.0/0     0.0.0.0/0
```

### Ver conexiones activas
```bash
sudo conntrack -L | grep ESTABLISHED

# Ejemplo:
tcp  6  299  ESTABLISHED src=192.168.1.10 dst=8.8.8.8 sport=45678 dport=53 \
     src=8.8.8.8 dst=200.1.2.3 sport=53 dport=12345 [ASSURED]
```

### Probar desde cliente
```bash
# Desde un dispositivo en la red LAN:
curl -v http://ipinfo.io/ip

# Debería mostrar la IP pública del gateway, no la IP privada del cliente
```

## 📈 Ventajas del MASQUERADE

1. **Múltiples clientes, una IP pública**
   - Cientos de dispositivos pueden compartir una sola IP
   
2. **Seguridad adicional**
   - IPs privadas no expuestas a internet
   - Firewall implícito (conexiones entrantes bloqueadas por defecto)

3. **Flexibilidad**
   - Funciona aunque la IP pública cambie (DHCP en WAN)
   - Útil para conexiones residenciales

4. **Ahorro de IPs**
   - No necesitas una IP pública por dispositivo

## 🔄 Diferencia: NAT vs MASQUERADE

| Característica | NAT (SNAT) | MASQUERADE |
|----------------|-----------|------------|
| IP pública fija | Sí | No (puede ser dinámica) |
| Rendimiento | Ligeramente mejor | Muy bueno |
| Uso típico | Servidores con IP estática | Routers domésticos |
| Comando | `--to-source 1.2.3.4` | `-j MASQUERADE` |

## ✅ Verificación del Requisito

- ✅ NAT/MASQUERADE funcional en interfaz WAN
- ✅ Múltiples clientes comparten IP pública del gateway
- ✅ Traducción bidireccional automática
- ✅ Detección automática de interfaz WAN
- ✅ Usa iptables (herramienta estándar de Linux)

## 🔧 Comandos Útiles

```bash
# Ver todas las reglas NAT
sudo iptables -t nat -L -v -n --line-numbers

# Eliminar regla específica (ej: línea 1)
sudo iptables -t nat -D POSTROUTING 1

# Agregar regla manualmente
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Limpiar todas las reglas NAT
sudo iptables -t nat -F

# Guardar reglas (persistencia)
sudo iptables-save > /etc/iptables/rules.v4
```
