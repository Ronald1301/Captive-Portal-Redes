#!/usr/bin/env python3
"""
Servidor HTTP para portal cautivo usando sockets puros.
Implementación manual sin usar http.server - solo sockets y threading.
Ejecutar con privilegios si se quiere que lance scripts de iptables.
"""
import os
import sys
import json
import threading
import socket
import secrets
from urllib.parse import parse_qs

from auth import verify_user, load_users

ROOT = os.path.dirname(__file__)
TEMPLATES = os.path.join(ROOT, 'templates')

# sessions: session_id -> {user, ip}
SESSIONS = {}
SESSIONS_LOCK = threading.Lock()


def load_template(name):
    """Carga un template HTML"""
    path = os.path.join(TEMPLATES, name)
    with open(path, 'rb') as f:
        return f.read()


def parse_cookies(cookie_header):
    """Parsea las cookies del header"""
    cookies = {}
    if not cookie_header:
        return cookies
    for item in cookie_header.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value
    return cookies


def parse_http_request(request_data):
    """Parsea la petición HTTP cruda"""
    try:
        # Separar headers y body
        if b'\r\n\r\n' not in request_data:
            return None, None, None, b''
        
        headers_part, body = request_data.split(b'\r\n\r\n', 1)
        lines = headers_part.split(b'\r\n')
        
        # Primera línea: método, path, versión
        request_line = lines[0].decode('utf-8', errors='ignore')
        parts = request_line.split()
        if len(parts) < 3:
            return None, None, None, b''
        
        method = parts[0]
        path = parts[1]
        
        # Headers
        headers = {}
        for line in lines[1:]:
            try:
                header_line = line.decode('utf-8', errors='ignore')
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    headers[key.strip()] = value.strip()
            except:
                continue
        
        return method, path, headers, body
    except Exception as e:
        print(f'Error parsing request: {e}')
        return None, None, None, b''


def is_authorized(headers, client_ip):
    """
    Verifica si el cliente está autorizado mediante verificación de token de sesión.
    """
    cookie_header = headers.get('Cookie', '')
    cookies = parse_cookies(cookie_header)
    
    session_id = cookies.get('CAPTIVE_SESSION')
    if not session_id:
        return False
    
    with SESSIONS_LOCK:
        session = SESSIONS.get(session_id)
    
    if not session:
        return False
    
    # Verificar que la IP coincida con la IP registrada en la sesión
    if session.get('ip') != client_ip:
        return False
    
    return True


def send_response(client_socket, status_code, status_text, headers, body):
    """Envía una respuesta HTTP"""
    try:
        # Línea de estado
        response = f'HTTP/1.1 {status_code} {status_text}\r\n'
        
        # Headers
        for key, value in headers.items():
            response += f'{key}: {value}\r\n'
        
        # Línea en blanco antes del body
        response += '\r\n'
        
        # Enviar headers
        client_socket.sendall(response.encode('utf-8'))
        
        # Enviar body si existe
        if body:
            if isinstance(body, str):
                body = body.encode('utf-8')
            client_socket.sendall(body)
    except Exception as e:
        print(f'Error sending response: {e}')


def handle_get_request(client_socket, path, headers, client_ip):
    """Maneja peticiones GET"""
    authorized = is_authorized(headers, client_ip)
    
    # Rutas del portal
    if path in ('/', '/index.html', '/login', '/success.html'):
        if not authorized:
            # Mostrar login
            body = load_template('index.html')
            response_headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': str(len(body)),
                'Connection': 'close'
            }
            send_response(client_socket, 200, 'OK', response_headers, body)
        else:
            # Mostrar página de éxito
            body = load_template('success.html')
            response_headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': str(len(body)),
                'Connection': 'close'
            }
            send_response(client_socket, 200, 'OK', response_headers, body)
    else:
        # Cualquier otra URL
        if not authorized:
            # Redirigir al portal
            response_headers = {
                'Location': '/',
                'Connection': 'close'
            }
            send_response(client_socket, 302, 'Found', response_headers, b'')
        else:
            # Ya está autenticado
            body = b'<html><body><h1>Access Granted</h1><p>You have internet access.</p></body></html>'
            response_headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': str(len(body)),
                'Connection': 'close'
            }
            send_response(client_socket, 200, 'OK', response_headers, body)


def handle_post_request(client_socket, path, headers, body, client_ip):
    """Maneja peticiones POST"""
    if path == '/login':
        # Parsear parámetros del body
        body_str = body.decode('utf-8', errors='ignore')
        params = parse_qs(body_str)
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        if verify_user(username, password):
            # Crear sesión con token seguro
            session_id = secrets.token_urlsafe(32)
            
            with SESSIONS_LOCK:
                SESSIONS[session_id] = {
                    'user': username,
                    'ip': client_ip
                }
            
            # Habilitar internet para esta IP
            try:
                import subprocess
                script_path = os.path.join(ROOT, 'scripts', 'enable_internet.sh')
                subprocess.Popen(['sudo', script_path, client_ip],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                print(f'✓ Access granted to {client_ip} (user: {username})')
            except Exception as e:
                print(f'⚠ Warning: Could not enable internet for {client_ip}: {e}')
            
            # Redirigir con cookie
            response_headers = {
                'Location': '/',
                'Set-Cookie': f'CAPTIVE_SESSION={session_id}; Path=/; HttpOnly',
                'Connection': 'close'
            }
            send_response(client_socket, 302, 'Found', response_headers, b'')
        else:
            # Login fallido
            body = b'<html><body><h1>Login Failed</h1><p>Invalid credentials</p><a href="/">Try again</a></body></html>'
            response_headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': str(len(body)),
                'Connection': 'close'
            }
            send_response(client_socket, 401, 'Unauthorized', response_headers, body)
    else:
        # 404 para otros paths
        body = b'<html><body><h1>404 Not Found</h1></body></html>'
        response_headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Content-Length': str(len(body)),
            'Connection': 'close'
        }
        send_response(client_socket, 404, 'Not Found', response_headers, body)


def handle_client(client_socket, client_address):
    """Maneja la conexión de un cliente (se ejecuta en un thread separado)"""
    client_ip = client_address[0]
    
    try:
        # Recibir datos del cliente
        request_data = b''
        client_socket.settimeout(5.0)  # Timeout de 5 segundos
        
        while True:
            try:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                request_data += chunk
                
                # Si encontramos el final de los headers, verificamos si necesitamos más datos
                if b'\r\n\r\n' in request_data:
                    # Buscar Content-Length
                    headers_end = request_data.index(b'\r\n\r\n')
                    headers_part = request_data[:headers_end].decode('utf-8', errors='ignore')
                    
                    content_length = 0
                    for line in headers_part.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            try:
                                content_length = int(line.split(':', 1)[1].strip())
                            except:
                                pass
                            break
                    
                    # Verificar si tenemos todo el body
                    body_start = headers_end + 4
                    body_received = len(request_data) - body_start
                    
                    if body_received >= content_length:
                        break
            except socket.timeout:
                break
        
        if not request_data:
            return
        
        # Parsear la petición HTTP
        method, path, headers, body = parse_http_request(request_data)
        
        if not method:
            return
        
        # Log de la petición
        print(f'{client_ip} - {method} {path}')
        
        # Procesar según el método HTTP
        if method == 'GET':
            handle_get_request(client_socket, path, headers, client_ip)
        elif method == 'POST':
            handle_post_request(client_socket, path, headers, body, client_ip)
        else:
            # Método no soportado
            body = b'<html><body><h1>405 Method Not Allowed</h1></body></html>'
            response_headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': str(len(body)),
                'Connection': 'close'
            }
            send_response(client_socket, 405, 'Method Not Allowed', response_headers, body)
    
    except Exception as e:
        print(f'Error handling client {client_ip}: {e}')
    
    finally:
        try:
            client_socket.close()
        except:
            pass


class CaptivePortalServer:
    """Servidor HTTP manual usando sockets puros"""
    
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
    
    def start(self):
        """Inicia el servidor"""
        # Crear socket TCP/IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permitir reusar la dirección inmediatamente después de cerrar
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind al host y puerto
        try:
            self.server_socket.bind((self.host, self.port))
        except Exception as e:
            print(f'❌ Error binding to {self.host}:{self.port}')
            print(f'   {e}')
            if self.port < 1024:
                print('   Ports below 1024 require root privileges. Run with sudo.')
            sys.exit(1)
        
        # Escuchar conexiones entrantes (backlog de 10 conexiones pendientes)
        self.server_socket.listen(10)
        
        self.running = True
        
        print('========================================')
        print('   CAPTIVE PORTAL SERVER (HTTP)')
        print('   (Manual Socket Implementation)')
        print('========================================')
        print(f'Listening on {self.host}:{self.port}')
        print(f'Users file: {os.path.join(ROOT, "users.json")}')
        print('Press Ctrl+C to stop')
        print('========================================')
        print('')
        
        # Loop principal: aceptar conexiones
        while self.running:
            try:
                # Aceptar una conexión entrante (bloqueante)
                client_socket, client_address = self.server_socket.accept()
                
                # Manejar el cliente en un thread separado (concurrencia)
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
            except KeyboardInterrupt:
                print('\n\nShutting down server...')
                break
            except Exception as e:
                if self.running:
                    print(f'Error accepting connection: {e}')
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass


def main():
    server = CaptivePortalServer(host='0.0.0.0', port=80)
    
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        print('✓ Server stopped')


if __name__ == '__main__':
    main()
