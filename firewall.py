import subprocess
import logging
from threading import Lock

class FirewallManager:
     
    
    def __init__(self, interface="eth0"):
         
        self.interface = interface
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def _run_command(self, command):
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                self.logger.error(f"Error ejecutando comando: {' '.join(command)}")
                self.logger.error(f"Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Excepción al ejecutar comando: {e}")
            return False
    
    def setup_initial_rules(self):
         
        with self.lock:
            # Permitir tráfico local
            self._run_command(["sysctl", "-w", "net.ipv4.ip_forward=1"])
            self._run_command(["iptables", "-A", "INPUT", "-i", "lo", "-j", "ACCEPT"])
            
            # Permitir conexiones establecidas y relacionadas SOLO desde el interior (origen)
            # Esto es más restrictivo que permitir en ambas direcciones
            self._run_command([
                "iptables", "-A", "FORWARD", "-m", "conntrack",
                "--ctstate", "ESTABLISHED,RELATED", "-j", "ACCEPT"
            ])
            
            # Bloquear todo el forwarding por defecto (política DROP)
            self._run_command(["iptables", "-P", "FORWARD", "DROP"])
            
            # Habilitar NAT para las conexiones autorizadas
            self._run_command([
                "iptables", "-t", "nat", "-A", "POSTROUTING",
                "-o", self.interface, "-j", "MASQUERADE"
            ])
            
            self.logger.info("Reglas iniciales de firewall configuradas")
    
    def allow_ip(self, ip_address):
         
        with self.lock:
            # Permitir forwarding desde esta IP
            success = self._run_command([
                "iptables", "-A", "FORWARD",
                "-s", ip_address, "-j", "ACCEPT"
            ])
            
            #  "iptables", "-I", "FORWARD", "1",
            #     "-s", ip_address, "-j", "ACCEPT"
            if success:
                self.logger.info(f"IP permitida: {ip_address}")
            
            return success

    def block_ip(self, ip_address):
         
        with self.lock:
            # Primero, eliminar conexiones establecidas de esta IP usando conntrack
            # Esto cierra inmediatamente los sockets TCP/UDP activos
            self._run_command([
                "conntrack", "-D", "-s", ip_address
            ])
            
            # Enviar RST (reset) a todas las conexiones TCP de esta IP
            # Para cerrar más agresivamente las conexiones existentes
            self._run_command([
                "iptables", "-A", "FORWARD",
                "-s", ip_address, "-j", "REJECT", "--reject-with", "tcp-reset"
            ])
            
            # Agregar regla de DROP explícito para bloquear todo tráfico desde esta IP
            self._run_command([
                "iptables", "-I", "FORWARD", "1",
                "-s", ip_address, "-j", "DROP"
            ])
            
            # También eliminar la regla de ACCEPT si existe
            self._run_command([
                "iptables", "-D", "FORWARD",
                "-s", ip_address, "-j", "ACCEPT"
            ])
            
            # Flush las conexiones de conntrack una vez más para asegurar
            self._run_command([
                "conntrack", "-D", "-s", ip_address
            ])
            
            self.logger.info(f"IP bloqueada y conexiones establecidas eliminadas: {ip_address}")
            
            return True
    
    def clear_rules(self):
         
        with self.lock:
            # Establecer políticas por defecto a ACCEPT
            self._run_command(["iptables", "-P", "INPUT", "ACCEPT"])
            self._run_command(["iptables", "-P", "FORWARD", "ACCEPT"])
            self._run_command(["iptables", "-P", "OUTPUT", "ACCEPT"])
            
            # Limpiar todas las reglas
            print("La pinga")
            self._run_command(["iptables", "-F"])
            self._run_command(["iptables", "-X"])
            
            # Limpiar reglas de NAT
            self._run_command(["iptables", "-t", "nat", "-F"])
            self._run_command(["iptables", "-t", "nat", "-X"])
            self._run_command(["sysctl", "-w", "net.ipv4.ip_forward=0"])
            self.logger.info("Reglas de firewall limpiadas")
    
    def list_allowed_ips(self):
         
        try:
            result = subprocess.run(
                ["iptables", "-L", "FORWARD", "-n", "-v"],
                capture_output=True,
                text=True,
                check=False
            )
            
            allowed_ips = []
            for line in result.stdout.split('\n'):
                if 'ACCEPT' in line and 'state ESTABLISHED,RELATED' not in line:
                    parts = line.split()
                    if len(parts) > 7:
                        ip = parts[7]
                        if ip != '0.0.0.0/0' and ip != 'anywhere':
                            allowed_ips.append(ip)
            
            return allowed_ips
        except Exception as e:
            self.logger.error(f"Error listando IPs permitidas: {e}")
            return []