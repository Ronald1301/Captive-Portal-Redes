#!/usr/bin/env python3
"""
Servidor DNS falso para portal cautivo.
Redirige todas las consultas DNS a la IP del gateway (este servidor).
"""
import socket
import struct
import threading
import argparse


class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''
        
        # Parsear el nombre de dominio de la consulta DNS
        tipo = (data[2] >> 3) & 15
        if tipo == 0:  # Query estándar
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += data[ini+1:ini+lon+1].decode('utf-8', errors='ignore') + '.'
                ini += lon + 1
                lon = data[ini]
    
    def response(self, ip):
        """Genera una respuesta DNS apuntando al IP especificado"""
        if not self.domain:
            return b''
        
        packet = b''
        packet += self.data[:2]  # Transaction ID
        packet += b'\x81\x80'  # Flags: respuesta estándar
        packet += self.data[4:6]  # Questions
        packet += self.data[4:6]  # Answer RRs (mismo que Questions)
        packet += b'\x00\x00'  # Authority RRs
        packet += b'\x00\x00'  # Additional RRs
        packet += self.data[12:]  # Query original
        
        # Respuesta: apuntar al IP del portal
        packet += b'\xc0\x0c'  # Pointer to domain name
        packet += b'\x00\x01'  # Type A
        packet += b'\x00\x01'  # Class IN
        packet += b'\x00\x00\x00\x3c'  # TTL (60 segundos)
        packet += b'\x00\x04'  # Data length (4 bytes para IPv4)
        
        # Convertir IP string a bytes
        packet += b''.join([struct.pack('!B', int(x)) for x in ip.split('.')])
        
        return packet


class DNSServer:
    def __init__(self, host='0.0.0.0', port=53, redirect_ip='192.168.1.1'):
        self.host = host
        self.port = port
        self.redirect_ip = redirect_ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
    
    def start(self):
        """Inicia el servidor DNS"""
        try:
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f'DNS Server listening on {self.host}:{self.port}')
            print(f'Redirecting all queries to {self.redirect_ip}')
            
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(512)
                    threading.Thread(target=self.handle_request, args=(data, addr), daemon=True).start()
                except Exception as e:
                    if self.running:
                        print(f'Error handling request: {e}')
        except Exception as e:
            print(f'Error starting DNS server: {e}')
            print('Make sure you have permission to bind to port 53 (run with sudo)')
        finally:
            self.sock.close()
    
    def handle_request(self, data, addr):
        """Maneja una consulta DNS"""
        try:
            query = DNSQuery(data)
            if query.domain:
                print(f'DNS Query from {addr[0]}: {query.domain} -> {self.redirect_ip}')
            response = query.response(self.redirect_ip)
            if response:
                self.sock.sendto(response, addr)
        except Exception as e:
            print(f'Error processing DNS query: {e}')
    
    def stop(self):
        """Detiene el servidor DNS"""
        self.running = False
        self.sock.close()


def parse_args():
    p = argparse.ArgumentParser(description='Fake DNS server for captive portal')
    p.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    p.add_argument('--port', type=int, default=53, help='Port to bind to')
    p.add_argument('--ip', required=True, help='IP address to redirect all queries to (gateway IP)')
    return p.parse_args()


def main():
    args = parse_args()
    server = DNSServer(host=args.host, port=args.port, redirect_ip=args.ip)
    try:
        server.start()
    except KeyboardInterrupt:
        print('\nShutting down DNS server...')
        server.stop()


if __name__ == '__main__':
    main()
