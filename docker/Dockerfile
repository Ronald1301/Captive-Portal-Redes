# Dockerfile para el portal cautivo
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias necesarias
RUN apt-get update && \
    apt-get install -y iproute2 iptables net-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar el proyecto
COPY . /app

EXPOSE 80

CMD ["python3", "server.py"]
