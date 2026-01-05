#!/usr/bin/env python3
"""
Servidor DNS falso para detección automática de portal cautivo.
Redirige todas las consultas DNS a la IP del portal (gateway).
Basado en la implementación de 'proyecto ronald'.
"""
import socket
import struct
import threading
import argparse
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''
        self.valid = False
        
        try:
            # Verificar que el paquete tenga al menos 12 bytes de header
            if len(data) < 12:
                return
            
            # Verificar que sea una consulta (tipo de mensaje)
            tipo = (data[2] >> 3) & 15
            if tipo == 0:  # Es una consulta
                self.valid = True
                ini = 12
                
                # Parsear el nombre de dominio
                while ini < len(data):
                    lon = data[ini]
                    if lon == 0:
                        break
                    if lon > 63:  # Validación: etiqueta no debe exceder 63 bytes
                        self.valid = False
                        break
                    
                    if ini + lon + 1 > len(data):
                        self.valid = False
                        break
                    
                    self.domain += data[ini+1:ini+lon+1].decode('utf-8', errors='ignore') + '.'
                    ini += lon + 1
        except Exception as e:
            logger.debug(f"Error parsing DNS query: {e}")
            self.valid = False

    def response(self, ip):
        """Construye una respuesta DNS que redirige al IP especificado."""
        if not self.domain or not self.valid:
            return b''
        
        try:
            # Respuesta DNS construida manualmente
            packet = b''
            # ID de transacción (copiado de la consulta)
            packet += self.data[:2]
            # Flags: respuesta (0x81), sin error (0x80)
            packet += b'\x81\x80'
            # Número de preguntas y respuestas
            packet += self.data[4:6]  # Preguntas
            packet += self.data[4:6]  # Una respuesta
            packet += b'\x00\x00'      # Sin registros de autoridad
            packet += b'\x00\x00'      # Sin registros adicionales
            # Sección de preguntas (copiada de la consulta)
            packet += self.data[12:]
            # Sección de respuestas
            packet += b'\xc0\x0c'      # Puntero al nombre en la pregunta
            packet += b'\x00\x01'      # Tipo A (dirección IPv4)
            packet += b'\x00\x01'      # Clase IN (Internet)
            packet += b'\x00\x00\x00\x3c'  # TTL: 60 segundos
            packet += b'\x00\x04'      # Longitud: 4 bytes (IPv4)
            # Dirección IP
            packet += b''.join([struct.pack('!B', int(x)) for x in ip.split('.')])
            
            return packet
        except Exception as e:
            logger.error(f"Error building DNS response: {e}")
            return b''

class DNSServer:
    def __init__(self, host='0.0.0.0', port=53, redirect_ip='192.168.137.1'):
        self.host = host
        self.port = port
        self.redirect_ip = redirect_ip
        self.sock = None
        self.running = False
        self.thread_count = 0
        self.max_threads = 100
    
    def start(self):
        """Inicia el servidor DNS."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(2.0)
            
            self.running = True
            logger.info(f"DNS Server listening on {self.host}:{self.port}")
            logger.info(f"Redirecting all queries to {self.redirect_ip}")
            
            self._accept_queries()
        except PermissionError:
            logger.error("ERROR: No tienes permisos para usar puerto 53. Ejecuta con sudo.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error starting DNS server: {e}")
            sys.exit(1)
        finally:
            self.stop()
    
    def _accept_queries(self):
        """Acepta consultas DNS entrantes."""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(512)
                
                # Limitar número de threads concurrentes
                if self.thread_count < self.max_threads:
                    self.thread_count += 1
                    thread = threading.Thread(
                        target=self._handle_request,
                        args=(data, addr),
                        daemon=True
                    )
                    thread.start()
                else:
                    logger.warning(f"Max threads reached ({self.max_threads}), dropping request from {addr[0]}")
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting DNS query: {e}")
    
    def _handle_request(self, data, addr):
        """Procesa una consulta DNS."""
        try:
            query = DNSQuery(data)
            
            if query.valid and query.domain:
                logger.debug(f"DNS Query from {addr[0]}: {query.domain.rstrip('.')} -> {self.redirect_ip}")
            
            response = query.response(self.redirect_ip)
            
            if response:
                self.sock.sendto(response, addr)
        except Exception as e:
            logger.error(f"Error processing DNS query from {addr[0]}: {e}")
        finally:
            self.thread_count -= 1
    
    def stop(self):
        """Detiene el servidor DNS."""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        logger.info("DNS server stopped")

def parse_args():
    p = argparse.ArgumentParser(description='Fake DNS server for captive portal detection')
    p.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    p.add_argument('--port', type=int, default=53, help='Port to bind to')
    p.add_argument('--ip', required=True, help='IP address to redirect all queries to (gateway IP)')
    p.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return p.parse_args()

def main():
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    server = DNSServer(host=args.host, port=args.port, redirect_ip=args.ip)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info('Shutting down DNS server...')
        server.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        server.stop()
        sys.exit(1)

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
