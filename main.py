import logging
import signal
import sys
import time
from threading import Thread

from users import UserManager
from sessions import SessionManager
from firewall import FirewallManager
from server import CaptivePortalServer

class CaptivePortal:
     
    
    def __init__(self, interface="eth0", port=80, session_timeout=3600):
         
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
        
        self.server = CaptivePortalServer(
            host='192.168.137.1',
            port=port,
            user_manager=self.user_manager,
            session_manager=self.session_manager,
            firewall_manager=self.firewall_manager
        )
        
        # Hilo para limpieza de sesiones
        self.cleanup_thread = None
        self.running = False

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
        INTERFACE = "eth0"  # Cambiar según tu interfaz de red
        PORT = 80          # Puerto HTTP (requiere privilegios de root)
        SESSION_TIMEOUT = 3600  # 1 hora
        
        # Verificar si se ejecuta como root (necesario para iptables)
        import os
        if os.geteuid() != 0:
            print("ERROR: Este script debe ejecutarse como root (sudo)")
            print("Uso: sudo python3 main.py")
            sys.exit(1)
        
        # Registrar manejador de señales
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Crear e iniciar portal
        portal = CaptivePortal(
            interface=INTERFACE,
            port=PORT,
            session_timeout=SESSION_TIMEOUT
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
