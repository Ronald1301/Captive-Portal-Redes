
"""
Módulo del servidor HTTP del portal cautivo.
Maneja las peticiones HTTP y el endpoint de login usando sockets.
"""

import socket
import logging
import os
from threading import Thread, Lock
from urllib.parse import parse_qs, urlparse, unquote

# Ruta de los templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class HTTPRequest:
    """Clase para parsear y representar una petición HTTP."""
    
    def __init__(self, raw_request):
        """Parsea la petición HTTP cruda."""
        lines = raw_request.split('\r\n')
        
        # Primera línea: método, path, versión
        request_line = lines[0].split(' ')
        self.method = request_line[0]
        self.path = request_line[1]
        self.version = request_line[2] if len(request_line) > 2 else 'HTTP/1.1'
        
        # Parsear headers
        self.headers = {}
        i = 1
        while i < len(lines) and lines[i]:
            if ':' in lines[i]:
                key, value = lines[i].split(':', 1)
                self.headers[key.strip().lower()] = value.strip()
            i += 1
        
        # Body (después de línea vacía)
        self.body = '\r\n'.join(lines[i+1:]) if i < len(lines) else ''


def load_template(template_name):
    """
    Carga un template HTML desde el directorio de templates.
    
    Args:
        template_name: Nombre del archivo template
        
    Returns:
        Contenido del template o None si no existe
    """
    try:
        template_path = os.path.join(TEMPLATES_DIR, template_name)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logging.error(f"Template no encontrado: {template_path}")
            return None
    except Exception as e:
        logging.error(f"Error cargando template {template_name}: {e}")
        return None


class CaptivePortalHandler:
    """Manejador de peticiones HTTP para el portal cautivo."""
    
    def __init__(self, client_socket, client_address, server):
        """
        Inicializa el handler.
        
        Args:
            client_socket: Socket del cliente
            client_address: Dirección del cliente
            server: Referencia al servidor
        """
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.logger = logging.getLogger(__name__)
    
    def handle(self):
        """Procesa la petición del cliente."""
        try:
            # Recibir datos del cliente
            raw_request = self.client_socket.recv(8192).decode('utf-8', errors='ignore')
            
            if not raw_request:
                return
            
            # Parsear la petición
            request = HTTPRequest(raw_request)
            
            self.logger.info(f"{self.client_address[0]} - {request.method} {request.path}")
            
            # Procesar según el método
            if request.method == 'GET':
                self.do_GET(request)
            elif request.method == 'POST':
                self.do_POST(request)
            else:
                self.send_error(405, 'Method Not Allowed')
                
        except Exception as e:
            self.logger.error(f"Error manejando petición: {e}")
            self.send_error(500, 'Internal Server Error')
        finally:
            self.client_socket.close()
    
    def send_response(self, status_code, status_message, headers, body):
        """
        Envía una respuesta HTTP al cliente.
        
        Args:
            status_code: Código de estado HTTP
            status_message: Mensaje de estado
            headers: Diccionario de headers
            body: Contenido de la respuesta
        """
        try:
            # Construir respuesta HTTP
            response = f"HTTP/1.1 {status_code} {status_message}\r\n"
            
            # Agregar headers
            for key, value in headers.items():
                response += f"{key}: {value}\r\n"
            
            response += "\r\n"
            
            # Enviar respuesta
            self.client_socket.sendall(response.encode('utf-8'))
            
            # Enviar body si existe
            if body:
                if isinstance(body, str):
                    self.client_socket.sendall(body.encode('utf-8'))
                else:
                    self.client_socket.sendall(body)
                    
        except Exception as e:
            self.logger.error(f"Error enviando respuesta: {e}")
    
    def send_error(self, status_code, message):
        """Envía una respuesta de error."""
        headers = {
            'Content-Type': 'text/html',
            'Connection': 'close'
        }
        body = f"<html><body><h1>{status_code} {message}</h1></body></html>"
        self.send_response(status_code, message, headers, body)
    
    def _get_client_ip(self):
        """Obtiene la dirección IP del cliente."""
        return self.client_address[0]
    
    def _get_login_page(self, message=""):
        """Carga y retorna la página HTML de login desde el template."""
        html = load_template('index.html')
        
        if html is None:
            # Fallback si el template no existe
            html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Cautivo - Error</title>
</head>
<body>
    <h1>Error: No se puede cargar el portal</h1>
    <p>El archivo de template no se encontró.</p>
</body>
</html>
            """
        
        return html
    
    def _get_success_page(self, username):
        """Carga y retorna la página HTML de éxito desde el template."""
        html = load_template('success.html')
        
        if html is None:
            # Fallback si el template no existe
            html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Cautivo - Acceso Concedido</title>
</head>
<body>
    <h1>¡Acceso Concedido!</h1>
    <p>Bienvenido, {username}</p>
    <p>Has iniciado sesión correctamente.</p>
</body>
</html>
            """
        
        return html
    
    def _get_register_page(self, message=""):
        """Carga y retorna la página HTML de registro desde el template."""
        html = load_template('register.html')
        
        if html is None:
            # Fallback si el template no existe
            html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Cautivo - Registro</title>
</head>
<body>
    <h1>Crear Cuenta</h1>
    <form method="post" action="/register">
        <label for="username">Usuario</label>
        <input type="text" id="username" name="username" required>
        <label for="email">Correo</label>
        <input type="email" id="email" name="email" required>
        <label for="password">Contraseña</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Registrarse</button>
    </form>
    <p><a href="/">Volver a login</a></p>
</body>
</html>
            """
        
        return html
    
    def do_GET(self, request):
        """Maneja las peticiones HTTP GET."""
        client_ip = self._get_client_ip()
        parsed_path = urlparse(request.path)
        
        # Manejar ruta de registro
        if parsed_path.path == '/register':
            body = self._get_register_page()
        # Verificar si ya está autenticado
        elif self.server.session_manager.is_authenticated(client_ip):
            username = self.server.session_manager.get_username_by_ip(client_ip)
            body = self._get_success_page(username)
        else:
            body = self._get_login_page()
        
        headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Content-Length': str(len(body.encode('utf-8'))),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Connection': 'close'
        }
        
        self.send_response(200, 'OK', headers, body)
    
    def do_POST(self, request):
        """Maneja las peticiones HTTP POST."""
        client_ip = self._get_client_ip()
        parsed_path = urlparse(request.path)
        
        # Manejar logout
        if parsed_path.path == '/logout':
            self.server.session_manager.end_session(client_ip)
            self.server.firewall_manager.block_ip(client_ip)
            
            body = self._get_login_page("Sesión cerrada correctamente")
            self.logger.info(f"Usuario desconectado desde {client_ip}")
        # Manejar registro de usuario
        elif parsed_path.path == '/register':
            # Parsear datos del formulario
            params = parse_qs(request.body)
            username = params.get('username', [''])[0]
            email = params.get('email', [''])[0]
            password = params.get('password', [''])[0]
            
            # Validar que todos los campos estén presentes
            if not username or not email or not password:
                body = self._get_register_page("Por favor completa todos los campos")
                self.logger.warning(f"Intento de registro incompleto desde {client_ip}")
            else:
                # Intentar registrar el usuario
                if self.server.user_manager.register(username, email, password):
                    # Registrar exitoso, crear sesión y autenticar
                    self.server.session_manager.create_session(client_ip, username)
                    self.server.firewall_manager.allow_ip(client_ip)
                    
                    self.logger.info(f"Nuevo usuario registrado: '{username}' desde {client_ip}")
                    body = self._get_success_page(username)
                else:
                    body = self._get_register_page("El usuario ya existe o hay un error en el registro")
                    self.logger.warning(f"Intento de registro fallido para usuario '{username}' desde {client_ip}")
        else:
            # Parsear datos del formulario (login)
            params = parse_qs(request.body)
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            
            # Autenticar usuario
            if self.server.user_manager.authenticate(username, password):
                self.server.session_manager.create_session(client_ip, username)
                self.server.firewall_manager.allow_ip(client_ip)
                
                self.logger.info(f"Usuario '{username}' autenticado desde {client_ip}")
                body = self._get_success_page(username)
            else:
                self.logger.warning(f"Intento de login fallido desde {client_ip} con usuario '{username}'")
                body = self._get_login_page("Usuario o contraseña incorrectos")
        
        headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Content-Length': str(len(body.encode('utf-8'))),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Connection': 'close'
        }
        
        self.send_response(200, 'OK', headers, body)


class CaptivePortalServer:
    """Servidor HTTP del portal cautivo usando sockets."""
    
    def __init__(self, host='0.0.0.0', port=80, user_manager=None, 
                 session_manager=None, firewall_manager=None):
        """
        Inicializa el servidor del portal cautivo.
        
        Args:
            host: Dirección en la que escuchar
            port: Puerto en el que escuchar
            user_manager: Instancia de UserManager
            session_manager: Instancia de SessionManager
            firewall_manager: Instancia de FirewallManager
        """
        self.host = host
        self.port = port
        self.user_manager = user_manager
        self.session_manager = session_manager
        self.firewall_manager = firewall_manager
        self.server_socket = None
        self.running = False
        self.server_thread = None
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Inicia el servidor HTTP."""
        try:
            # Crear socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind y listen
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            
            # Ejecutar en un hilo separado
            self.server_thread = Thread(target=self._accept_connections, daemon=True)
            self.server_thread.start()
            
            self.logger.info(f"Servidor HTTP iniciado en {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Error iniciando servidor: {e}")
            raise
    
    def _accept_connections(self):
        """Acepta conexiones entrantes."""
        self.logger.info("Esperando conexiones...")
        
        while self.running:
            try:
                # Timeout para poder verificar self.running periódicamente
                self.server_socket.settimeout(1.0)
                
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Manejar cada cliente en un hilo separado
                    client_thread = Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                    
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error aceptando conexión: {e}")
    
    def _handle_client(self, client_socket, client_address):
        """
        Maneja un cliente individual.
        
        Args:
            client_socket: Socket del cliente
            client_address: Dirección del cliente
        """
        handler = CaptivePortalHandler(client_socket, client_address, self)
        handler.handle()
    
    def stop(self):
        """Detiene el servidor HTTP."""
        self.logger.info("Deteniendo servidor HTTP...")
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        self.logger.info("Servidor HTTP detenido")







# """
# Módulo del servidor HTTP del portal cautivo.
# Maneja las peticiones HTTP y el endpoint de login.
# """

# from http.server import HTTPServer, BaseHTTPRequestHandler
# from urllib.parse import parse_qs, urlparse
# import json
# import logging
# from threading import Thread


# class CaptivePortalHandler(BaseHTTPRequestHandler):
#     """Manejador de peticiones HTTP para el portal cautivo."""
    
#     def log_message(self, format, *args):
#         """Sobrescribe el método de logging por defecto."""
#         logging.info(f"{self.address_string()} - {format % args}")
    
#     def _set_headers(self, content_type='text/html', status_code=200):
#         """
#         Establece las cabeceras HTTP de la respuesta.
        
#         Args:
#             content_type: Tipo de contenido MIME
#             status_code: Código de estado HTTP
#         """
#         self.send_response(status_code)
#         self.send_header('Content-type', content_type)
#         self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
#         self.send_header('Pragma', 'no-cache')
#         self.send_header('Expires', '0')
#         self.end_headers()
    
#     def _get_client_ip(self):
#         """
#         Obtiene la dirección IP del cliente.
        
#         Returns:
#             Dirección IP del cliente
#         """
#         return self.client_address[0]
    
#     def _get_login_page(self, message=""):
#         """
#         Genera la página HTML de login.
        
#         Args:
#             message: Mensaje a mostrar al usuario
            
#         Returns:
#             Código HTML de la página de login
#         """
#         html = f"""
# <!DOCTYPE html>
# <html lang="es">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Portal Cautivo - Iniciar Sesión</title>
#     <style>
#         * {{
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }}
#         body {{
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             min-height: 100vh;
#             padding: 20px;
#         }}
#         .container {{
#             background: white;
#             padding: 40px;
#             border-radius: 10px;
#             box-shadow: 0 10px 25px rgba(0,0,0,0.2);
#             max-width: 400px;
#             width: 100%;
#         }}
#         h1 {{
#             color: #333;
#             margin-bottom: 10px;
#             text-align: center;
#         }}
#         .subtitle {{
#             color: #666;
#             text-align: center;
#             margin-bottom: 30px;
#             font-size: 14px;
#         }}
#         .form-group {{
#             margin-bottom: 20px;
#         }}
#         label {{
#             display: block;
#             color: #555;
#             margin-bottom: 5px;
#             font-weight: 500;
#         }}
#         input[type="text"],
#         input[type="password"] {{
#             width: 100%;
#             padding: 12px;
#             border: 2px solid #e0e0e0;
#             border-radius: 5px;
#             font-size: 14px;
#             transition: border-color 0.3s;
#         }}
#         input[type="text"]:focus,
#         input[type="password"]:focus {{
#             outline: none;
#             border-color: #667eea;
#         }}
#         button {{
#             width: 100%;
#             padding: 12px;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             border: none;
#             border-radius: 5px;
#             font-size: 16px;
#             font-weight: 600;
#             cursor: pointer;
#             transition: transform 0.2s;
#         }}
#         button:hover {{
#             transform: translateY(-2px);
#         }}
#         button:active {{
#             transform: translateY(0);
#         }}
#         .message {{
#             padding: 10px;
#             margin-bottom: 20px;
#             border-radius: 5px;
#             text-align: center;
#         }}
#         .error {{
#             background: #fee;
#             color: #c33;
#             border: 1px solid #fcc;
#         }}
#         .success {{
#             background: #efe;
#             color: #3c3;
#             border: 1px solid #cfc;
#         }}
#         .info {{
#             background: #def;
#             color: #36c;
#             border: 1px solid #bcf;
#             margin-top: 20px;
#             font-size: 12px;
#         }}
#     </style>
# </head>
# <body>
#     <div class="container">
#         <h1>🔒 Portal Cautivo</h1>
#         <p class="subtitle">Inicia sesión para acceder a la red</p>
        
#         {"<div class='message error'>" + message + "</div>" if message else ""}
        
#         <form method="POST" action="/login">
#             <div class="form-group">
#                 <label for="username">Usuario</label>
#                 <input type="text" id="username" name="username" required autofocus>
#             </div>
            
#             <div class="form-group">
#                 <label for="password">Contraseña</label>
#                 <input type="password" id="password" name="password" required>
#             </div>
            
#             <button type="submit">Iniciar Sesión</button>
#         </form>
        
#         <div class="info">
#             <strong>Usuarios de prueba:</strong><br>
#             admin / admin123<br>
#             usuario1 / pass1234<br>
#             usuario2 / pass5678
#         </div>
#     </div>
# </body>
# </html>
#         """
#         return html
    
#     def _get_success_page(self, username):
#         """
#         Genera la página HTML de éxito tras el login.
        
#         Args:
#             username: Nombre del usuario autenticado
            
#         Returns:
#             Código HTML de la página de éxito
#         """
#         html = f"""
#     <!DOCTYPE html>
#     <html lang="es">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Portal Cautivo - Acceso Concedido</title>
#         <style>
#             * {{
#                 margin: 0;
#                 padding: 0;
#                 box-sizing: border-box;
#             }}
#             body {{
#                 font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#                 background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 min-height: 100vh;
#                 padding: 20px;
#             }}
#             .container {{
#                 background: white;
#                 padding: 40px;
#                 border-radius: 10px;
#                 box-shadow: 0 10px 25px rgba(0,0,0,0.2);
#                 max-width: 500px;
#                 width: 100%;
#                 text-align: center;
#             }}
#             h1 {{
#                 color: #333;
#                 margin-bottom: 10px;
#             }}
#             .success-icon {{
#                 font-size: 64px;
#                 margin-bottom: 20px;
#             }}
#             .username {{
#                 color: #11998e;
#                 font-weight: 600;
#                 font-size: 20px;
#                 margin-bottom: 20px;
#             }}
#             .message {{
#                 color: #666;
#                 margin-bottom: 30px;
#                 line-height: 1.6;
#             }}
#             .button {{
#                 display: inline-block;
#                 padding: 12px 30px;
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 color: white;
#                 text-decoration: none;
#                 border-radius: 5px;
#                 font-weight: 600;
#                 transition: transform 0.2s;
#                 border: none;
#                 cursor: pointer;
#                 font-size: 16px;
#             }}
#             .button:hover {{
#                 transform: translateY(-2px);
#             }}
#             .button:active {{
#                 transform: translateY(0);
#             }}
#             .logout-button {{
#                 background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#                 margin-top: 15px;
#             }}
#             .info {{
#                 background: #e8f5e9;
#                 padding: 15px;
#                 border-radius: 5px;
#                 margin-top: 20px;
#                 font-size: 14px;
#                 color: #2e7d32;
#             }}
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="success-icon">✅</div>
#             <h1>¡Acceso Concedido!</h1>
#             <div class="username">Bienvenido, {username}</div>
#             <div class="message">
#                 Has iniciado sesión correctamente.<br>
#                 Ahora tienes acceso completo a Internet.
#             </div>
#             <a href="https://www.google.com" class="button">Ir a Internet</a>
#             <br>
#             <form method="POST" action="/logout" style="display: inline;">
#                 <button type="submit" class="button logout-button">Cerrar Sesión</button>
#             </form>
#             <div class="info">
#                 Tu sesión se cerrará automáticamente después de un período de inactividad.
#             </div>
#         </div>
#     </body>
#     </html>
#         """
#         return html
    
#     def do_GET(self):
#         """Maneja las peticiones HTTP GET."""
#         client_ip = self._get_client_ip()
        
#         # Obtener referencias a los managers desde el servidor
#         session_manager = self.server.session_manager
        
#         # Verificar si ya está autenticado
#         if session_manager.is_authenticated(client_ip):
#             username = session_manager.get_username_by_ip(client_ip)
#             self._set_headers()
#             self.wfile.write(self._get_success_page(username).encode())
#         else:
#             # Mostrar página de login
#             self._set_headers()
#             self.wfile.write(self._get_login_page().encode())
    
#     def do_POST(self):
#         """Maneja las peticiones HTTP POST."""
#         client_ip = self._get_client_ip()
#         parsed_path = urlparse(self.path)
    
#     # Manejar logout
#         if parsed_path.path == '/logout':
#             # Terminar sesión
#             self.server.session_manager.end_session(client_ip)
            
#             # Bloquear IP en el firewall
#             self.server.firewall_manager.block_ip(client_ip)
            
#             # Redirigir a página de login con mensaje
#             self._set_headers()
#             self.wfile.write(self._get_login_page("Sesión cerrada correctamente").encode())
#             logging.info(f"Usuario desconectado desde {client_ip}")
#             return
        
#         # Leer el contenido del POST
#         content_length = int(self.headers['Content-Length'])
#         post_data = self.rfile.read(content_length).decode('utf-8')
#         params = parse_qs(post_data)
        
#         # Obtener credenciales
#         username = params.get('username', [''])[0]
#         password = params.get('password', [''])[0]
        
#         # Obtener referencias a los managers desde el servidor
#         user_manager = self.server.user_manager
#         session_manager = self.server.session_manager
#         firewall_manager = self.server.firewall_manager
        
#         # Autenticar usuario
#         if user_manager.authenticate(username, password):
#             # Crear sesión
#             session_manager.create_session(client_ip, username)
            
#             # Permitir acceso en el firewall
#             firewall_manager.allow_ip(client_ip)
            
#             logging.info(f"Usuario '{username}' autenticado desde {client_ip}")
            
#             # Mostrar página de éxito
#             self._set_headers()
#             self.wfile.write(self._get_success_page(username).encode())
#         else:
#             # Autenticación fallida
#             logging.warning(f"Intento de login fallido desde {client_ip} con usuario '{username}'")
            
#             self._set_headers()
#             self.wfile.write(self._get_login_page("Usuario o contraseña incorrectos").encode())


# class CaptivePortalServer:
#     """Servidor HTTP del portal cautivo con soporte multihilo."""
    
#     def __init__(self, host='0.0.0.0', port=80, user_manager=None, 
#                  session_manager=None, firewall_manager=None):
#         """
#         Inicializa el servidor del portal cautivo.
        
#         Args:
#             host: Dirección en la que escuchar
#             port: Puerto en el que escuchar
#             user_manager: Instancia de UserManager
#             session_manager: Instancia de SessionManager
#             firewall_manager: Instancia de FirewallManager
#         """
#         self.host = host
#         self.port = port
#         self.user_manager = user_manager
#         self.session_manager = session_manager
#         self.firewall_manager = firewall_manager
#         self.server = None
#         self.server_thread = None
    
#     def start(self):
#         """Inicia el servidor HTTP."""
#         self.server = HTTPServer((self.host, self.port), CaptivePortalHandler)
        
#         # Adjuntar los managers al servidor para que el handler pueda acceder
#         self.server.user_manager = self.user_manager
#         self.server.session_manager = self.session_manager
#         self.server.firewall_manager = self.firewall_manager
        
#         # Ejecutar en un hilo separado
#         self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
#         self.server_thread.start()
        
#         logging.info(f"Servidor HTTP iniciado en {self.host}:{self.port}")
    
#     def stop(self):
#         """Detiene el servidor HTTP."""
#         if self.server:
#             self.server.shutdown()
#             self.server.server_close()
#             logging.info("Servidor HTTP detenido")

