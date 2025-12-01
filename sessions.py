import time
from threading import Lock
from datetime import datetime, timedelta

class SessionManager:
     
    
    def __init__(self, session_timeout=3600):
         
        self.sessions = {}  # {ip_address: {'username': str, 'login_time': float, 'last_activity': float}}
        self.lock = Lock()
        self.session_timeout = session_timeout
    
    def create_session(self, ip_address, username):
         
        with self.lock:
            current_time = time.time()
            self.sessions[ip_address] = {
                'username': username,
                'login_time': current_time,
                'last_activity': current_time
            }
            return True
    
    def is_authenticated(self, ip_address):
         
        with self.lock:
            if ip_address not in self.sessions:
                return False
            
            session = self.sessions[ip_address]
            current_time = time.time()
            
            # Verificar si la sesión ha expirado
            if current_time - session['last_activity'] > self.session_timeout:
                del self.sessions[ip_address]
                return False
            
            # Actualizar última actividad
            session['last_activity'] = current_time
            return True
    
    def get_session_info(self, ip_address):
         
        with self.lock:
            if ip_address not in self.sessions:
                return None
            
            session = self.sessions[ip_address]
            return {
                'username': session['username'],
                'login_time': datetime.fromtimestamp(session['login_time']).strftime('%Y-%m-%d %H:%M:%S'),
                'last_activity': datetime.fromtimestamp(session['last_activity']).strftime('%Y-%m-%d %H:%M:%S'),
                'active': time.time() - session['last_activity'] <= self.session_timeout
            }
    
    def end_session(self, ip_address):
         
        with self.lock:
            if ip_address in self.sessions:
                del self.sessions[ip_address]
                return True
            return False
    
    def get_all_sessions(self):
         
        with self.lock:
            result = {}
            current_time = time.time()
            
            # Crear copia de las sesiones para no mantener el lock demasiado tiempo
            for ip, session in list(self.sessions.items()):
                if current_time - session['last_activity'] <= self.session_timeout:
                    result[ip] = {
                        'username': session['username'],
                        'login_time': datetime.fromtimestamp(session['login_time']).strftime('%Y-%m-%d %H:%M:%S'),
                        'last_activity': datetime.fromtimestamp(session['last_activity']).strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            return result
    
    def cleanup_expired_sessions(self):
         
        with self.lock:
            current_time = time.time()
            expired_ips = []
            
            for ip, session in list(self.sessions.items()):
                if current_time - session['last_activity'] > self.session_timeout:
                    expired_ips.append(ip)
                    del self.sessions[ip]
            
            return expired_ips
    
    def get_session_count(self):
         
        with self.lock:
            return len(self.sessions)
    
    def get_username_by_ip(self, ip_address):
         
        with self.lock:
            if ip_address in self.sessions:
                return self.sessions[ip_address]['username']
            return None