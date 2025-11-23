#!/bin/bash
# Script para crear red, contenedores y probar el portal cautivo

set -e

# Nombre de la red y subred
NET_NAME="captive-net"
SUBNET="192.168.100.0/24"
GATEWAY="192.168.100.1"

# Crear red macvlan (mejor para simular clientes reales)
docker network create -d macvlan \
  --subnet=$SUBNET \
  --gateway=$GATEWAY \
  -o parent=eth0 $NET_NAME

echo "✓ Red $NET_NAME creada con macvlan (ideal para simular clientes reales en la misma red física)"

echo "Construyendo imagen del portal cautivo..."
docker build -t captive-portal .

echo "Construyendo imagen de cliente..."
docker build -f Dockerfile.client -t captive-client .

# Crear contenedor del portal cautivo
docker run -d --name portal --network $NET_NAME --ip 192.168.100.10 --privileged -p 80:80 captive-portal

echo "✓ Contenedor portal cautivo iniciado (acceso a terminal: docker exec -it portal bash)"

# Crear clientes
for i in 1 2; do
  docker run -d --name client$i --network $NET_NAME --ip 192.168.100.2$i --privileged captive-client
  echo "✓ Cliente client$i creado (acceso a terminal: docker exec -it client$i bash)"
done

echo "Para probar el portal, abre Firefox en los clientes (docker exec -it client1 firefox &)."
echo "Accede a http://192.168.100.10 desde el navegador del cliente."
echo "Verifica que no tienes acceso a internet antes de loguearte."
echo "Después de loguearte, deberías tener acceso a internet."
