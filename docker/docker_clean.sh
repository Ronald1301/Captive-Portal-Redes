#!/bin/bash
# Script para limpiar el entorno de pruebas Docker del portal cautivo

set -e

# Detener y eliminar contenedores
for c in portal client1 client2; do
  if docker ps -a --format '{{.Names}}' | grep -q "^$c$"; then
    echo "Eliminando contenedor $c..."
    docker rm -f $c
  fi

done

# Eliminar red
NET_NAME="captive-net"
if docker network ls --format '{{.Name}}' | grep -q "^$NET_NAME$"; then
  echo "Eliminando red $NET_NAME..."
  docker network rm $NET_NAME
fi

echo "✓ Entorno Docker limpio. Puedes volver a ejecutar docker_test.sh para nuevas pruebas."
