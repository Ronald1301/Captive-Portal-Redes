# Guía de Pruebas del Portal Cautivo (Proyecto Ronald)

Este documento detalla los pasos para probar el portal cautivo en el escenario VM + hotspot de teléfono + laptop, siguiendo la arquitectura modular y centralizada de reglas iptables.

## 1. Requisitos Previos

- VM Linux (Ubuntu/Debian recomendado)
- Teléfono con hotspot WiFi
- Laptop conectada al hotspot
- Acceso root/sudo en la VM
- Scripts actualizados (flush centralizado, NAT/MASQUERADE, etc.)

## 2. Preparación de la Red

1. Activa el hotspot en el teléfono.
2. Conecta la VM y la laptop al hotspot.
3. Verifica interfaces en la VM:
   - `eth0` (LAN interna)
   - `wlan0` (hotspot)
4. Comprueba conectividad entre VM, laptop y teléfono (ping).

## 3. Configuración de Scripts

1. Verifica que los scripts estén actualizados:
   - `start_captive_portal.sh` (limpia reglas iptables al inicio)
   - `nat_setup.sh` (agrega MASQUERADE)
   - `disable_internet.sh` (solo agrega reglas, no limpia)
2. Da permisos de ejecución:
   ```bash
   chmod +x scripts/*.sh
   ```

## 4. Inicio del Portal Cautivo

1. Ejecuta:
   ```bash
   sudo ./scripts/start_captive_portal.sh
   ```
2. Verifica que los servicios estén activos:
   - Servidor DNS
   - Servidor web
3. Comprueba reglas iptables:
   ```bash
   sudo iptables -L -n -v
   sudo iptables -t nat -L -n -v
   ```

## 5. Pruebas de Acceso

1. Desde la laptop, navega a cualquier sitio web.
2. Debes ser redirigido al portal cautivo.
3. Haz login con credenciales válidas (`users.json`).
4. Verifica acceso a Internet tras autenticación.
5. Prueba logout y verifica que el acceso se bloquea.

## 6. Validación de NAT y Routing

1. En la VM, ejecuta:
   ```bash
   sudo iptables -t nat -L POSTROUTING
   ```
   - Debe aparecer la regla MASQUERADE.
2. Desde la laptop, verifica acceso tras login.
3. Si falla, revisa logs y reglas iptables.

## 7. Detención y Reinicio

1. Para detener el portal:
   ```bash
   sudo ./scripts/stop_captive_portal.sh
   ```
2. Reinicia el proceso si es necesario.

## 8. Solución de Problemas

- Revisa logs y reglas iptables.
- Consulta la documentación: `PROBLEMA-ENRUTAMIENTO-SOLUCIONADO.md`, `SOLUCION-MEJORADA-FLUSH-CENTRALIZADO.md`.

---

**Notas:**
- Este procedimiento asume la arquitectura modular y limpieza centralizada de reglas.
- Revisa scripts y documentación si tienes dudas.
