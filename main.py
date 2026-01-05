import logging
import signal
import sys
import time

from threading import Thread
import subprocess
import os

from users import UserManager
from sessions import SessionManager
from firewall import FirewallManager

from server import CaptivePortalServer

# Hilo para servidor DNS falso
class DNSFakeServerThread(Thread):
    def __init__(self, ip_gateway):
        super().__init__(daemon=True)
        self.ip_gateway = ip_gateway
        self.process = None
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Inicia el servidor DNS en un subprocess."""
        try:
            self.logger.info(f"Iniciando proceso DNS con puerta de enlace: {self.ip_gateway}")
            self.process = subprocess.Popen([
                sys.executable, 
                os.path.join(os.path.dirname(__file__), 'dns_server.py'),
                '--ip', self.ip_gateway
            ])
            self.logger.info(f"Proceso DNS iniciado con PID: {self.process.pid}")
            
            # Esperar a que el proceso termine
            self.process.wait()
            self.logger.warning("Proceso DNS terminó inesperadamente")
        except Exception as e:
            self.logger.error(f"Error iniciando proceso DNS: {e}")

    def stop(self):
        """Detiene el servidor DNS."""
        if self.process:
            try:
                self.logger.info("Terminando proceso DNS...")
                self.process.terminate()
                self.process.wait(timeout=5)
                self.logger.info("Proceso DNS terminado correctamente")
            except subprocess.TimeoutExpired:
                self.logger.warning("Timeout esperando DNS, forzando kill...")
                self.process.kill()
            except Exception as e:
                self.logger.error(f"Error deteniendo DNS: {e}")

class CaptivePortal:
     
    
    def __init__(self, interface="eth0", port=80, session_timeout=3600, gateway_ip=None):
         
        self.interface = interface
        self.port = port
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.logger.info("Inicializando componentes del portal cautivo...")
        
        self.user_manager = UserManager()
        self.session_manager = SessionManager(session_timeout=session_timeout)
        self.firewall_manager = FirewallManager(interface=interface)
        
        # Usar IP de gateway proporcionada o usar default
        if gateway_ip is None:
            self.gateway_ip = self._get_gateway_ip()
        else:
            self.gateway_ip = gateway_ip
        
        self.logger.info(f"IP del Gateway (Portal): {self.gateway_ip}")
        
        self.server = CaptivePortalServer(
            host=self.gateway_ip,
            port=port,
            user_manager=self.user_manager,
            session_manager=self.session_manager,
            firewall_manager=self.firewall_manager
        )
        self.dns_thread = DNSFakeServerThread(ip_gateway=self.gateway_ip)
        
        # Hilo para limpieza de sesiones
        self.cleanup_thread = None
        self.running = False
    
    def _get_gateway_ip(self):
        """
        Intenta obtener la IP del gateway (interfaz local).
        Si falla, devuelve una IP por defecto.
        """
        try:
            import socket
            hostname = socket.gethostname()
            gateway_ip = socket.gethostbyname(hostname)
            self.logger.info(f"IP del gateway detectada: {gateway_ip}")
            return gateway_ip
        except Exception as e:
            self.logger.warning(f"No se pudo detectar la IP del gateway: {e}")
            default_ip = '192.168.137.1'
            self.logger.warning(f"Usando IP por defecto: {default_ip}")
            return default_ip

    def setup(self):
         
        self.logger.info("Configurando reglas de firewall...")
        self.firewall_manager.setup_initial_rules()
        self.logger.info("Firewall configurado correctamente")
    
    def start(self):
         
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO PORTAL CAUTIVO")
        self.logger.info("=" * 60)
        
        # Configurar firewall
        self.setup()
        # Iniciar servidor DNS falso para detección automática
        self.logger.info("Iniciando servidor DNS falso para detección automática de portal cautivo...")
        self.dns_thread.start()
        # Iniciar servidor HTTP
        self.server.start()
        # Iniciar hilo de limpieza de sesiones
        self.running = True
        self.cleanup_thread = Thread(target=self._cleanup_sessions_loop, daemon=True)
        self.cleanup_thread.start()
        self.logger.info(f"Portal cautivo activo en puerto {self.port}")
        self.logger.info(f"Interfaz de red: {self.interface}")
        self.logger.info(f"Usuarios registrados: {len(self.user_manager.list_users())}")
        self.logger.info("=" * 60)
        self.logger.info("Presiona Ctrl+C para detener el servidor")
        self.logger.info("=" * 60)
    
    def stop(self):
         
        self.logger.info("\nDeteniendo portal cautivo...")
        
        # Detener servidor HTTP
        self.server.stop()
        # Detener servidor DNS falso
        self.logger.info("Deteniendo servidor DNS falso...")
        self.dns_thread.stop()
        # Detener hilo de limpieza
        self.running = False
        # Bloquear todas las IPs autenticadas
        self.logger.info("Revocando accesos...")
        for ip in list(self.session_manager.sessions.keys()):
            self.firewall_manager.block_ip(ip)
        # Limpiar reglas de firewall
        self.logger.info("Limpiando reglas de firewall...")
        self.firewall_manager.clear_rules()
        self.logger.info("Portal cautivo detenido correctamente")
    
    def _cleanup_sessions_loop(self):
         
        while self.running:
            time.sleep(60)  # Verificar cada minuto
            
            expired_ips = self.session_manager.cleanup_expired_sessions()
            
            for ip in expired_ips:
                self.logger.info(f"Sesión expirada para IP: {ip}")
                self.firewall_manager.block_ip(ip)
    
    def status(self):
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("ESTADO DEL PORTAL CAUTIVO")
        self.logger.info("=" * 60)
        
        # Sesiones activas
        sessions = self.session_manager.get_all_sessions()
        self.logger.info(f"Sesiones activas: {len(sessions)}")
        
        for ip, info in sessions.items():
            self.logger.info(f"  - {ip}: {info['username']} (login: {info['login_time']})")
        
        # Usuarios registrados
        users = self.user_manager.list_users()
        self.logger.info(f"\nUsuarios registrados: {len(users)}")
        for user in users:
            self.logger.info(f"  - {user}")
        
        # IPs permitidas
        allowed_ips = self.firewall_manager.list_allowed_ips()
        self.logger.info(f"\nIPs con acceso permitido: {len(allowed_ips)}")
        for ip in allowed_ips:
            self.logger.info(f"  - {ip}")
        
        self.logger.info("=" * 60 + "\n")


def signal_handler(sig, frame):
     
    print("\n\nSeñal de interrupción recibida...")
    if portal:
        portal.stop()
    sys.exit(0)


if __name__ == "__main__":
    portal = None
    
    try:
        # Configuración
        INTERFACE = "eth0"         # Cambiar según tu interfaz de red
        PORT = 80                  # Puerto HTTP (requiere privilegios de root)
        SESSION_TIMEOUT = 3600     # 1 hora
        GATEWAY_IP = None          # Dejar None para auto-detectar, o especificar manualmente
        
        # Verificar si se ejecuta como root (necesario para iptables y DNS)
        import os
        if os.geteuid() != 0:
            print("ERROR: Este script debe ejecutarse como root (sudo)")
            print("Uso: sudo python3 main.py [--gateway-ip IP]")
            sys.exit(1)
        
        # Parsear argumentos de línea de comandos
        if len(sys.argv) > 1:
            if sys.argv[1] == '--gateway-ip' and len(sys.argv) > 2:
                GATEWAY_IP = sys.argv[2]
                print(f"IP del gateway especificada: {GATEWAY_IP}")
            elif sys.argv[1] in ['-h', '--help']:
                print("Uso: sudo python3 main.py [opciones]")
                print("\nOpciones:")
                print("  --gateway-ip IP    Especificar IP del gateway (default: auto-detectar)")
                print("  -h, --help         Mostrar esta ayuda")
                sys.exit(0)
        
        # Registrar manejador de señales
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Crear e iniciar portal
        portal = CaptivePortal(
            interface=INTERFACE,
            port=PORT,
            session_timeout=SESSION_TIMEOUT,
            gateway_ip=GATEWAY_IP
        )
        
        portal.start()
        
        # Mantener el programa en ejecución
        while True:
            time.sleep(10)
            # Opcionalmente mostrar estado cada cierto tiempo
            # portal.status()
    
    except KeyboardInterrupt:
        print("\n\nInterrupción del teclado detectada...")
        if portal:
            portal.stop()
    
    except Exception as e:
        print(f"\nError fatal: {e}")
        if portal:
            portal.stop()
        sys.exit(1)
