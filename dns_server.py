"""
Archivo de arranque para el servidor DNS del portal cautivo.
Toda la lógica está segmentada en la carpeta dns_server/.
Este archivo solo importa y ejecuta el servidor segmentado.
"""

from dns_server.server import DNSServer

if __name__ == "__main__":
    # Puedes ajustar la IP de respuesta según tu red
    dns = DNSServer(listen_ip='0.0.0.0', port=53, response_ip='192.168.1.1')
    dns.serve_forever()
    
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
