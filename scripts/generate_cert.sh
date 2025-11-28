#!/bin/bash
# Script para generar certificados SSL autofirmados para el portal cautivo

CERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/certs"
DAYS=365

echo "========================================="
echo "   Generando Certificados SSL"
echo "========================================="
echo ""

# Crear directorio para certificados
mkdir -p "$CERT_DIR"

# Generar clave privada y certificado autofirmado
echo "Generando certificado autofirmado válido por $DAYS días..."

openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -days $DAYS \
    -subj "/C=DO/ST=SantoDomingo/L=SantoDomingo/O=Universidad/OU=Redes/CN=captive.portal.local"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Certificados generados exitosamente en: $CERT_DIR"
    echo "  - Clave privada: server.key"
    echo "  - Certificado: server.crt"
    echo ""
    echo "NOTA: Este es un certificado autofirmado. Los navegadores"
    echo "      mostrarán una advertencia de seguridad. Para un entorno"
    echo "      de producción, usa certificados válidos (Let's Encrypt)."
else
    echo ""
    echo "❌ ERROR: No se pudieron generar los certificados"
    echo "   Asegúrate de tener openssl instalado: sudo apt install openssl"
    exit 1
fi
