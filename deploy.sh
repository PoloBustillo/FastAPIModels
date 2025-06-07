#!/bin/bash
# deploy.sh - Script para deployment manual

set -e

# Variables de configuración
SERVER_HOST="tu-servidor.com"
SERVER_USER="tu-usuario"
SERVER_PATH="/opt/fastapi-app"
APP_NAME="fastapi-app"

echo "🚀 Iniciando deployment de FastAPI..."

# Construir imagen Docker
echo "📦 Construyendo imagen Docker..."
docker build -t $APP_NAME:latest .

# Guardar imagen como archivo
echo "💾 Guardando imagen Docker..."
docker save $APP_NAME:latest | gzip > $APP_NAME.tar.gz

# Copiar archivos al servidor
echo "📤 Copiando archivos al servidor..."
scp $APP_NAME.tar.gz $SERVER_USER@$SERVER_HOST:$SERVER_PATH/
scp docker-compose.prod.yml $SERVER_USER@$SERVER_HOST:$SERVER_PATH/
scp nginx.conf $SERVER_USER@$SERVER_HOST:$SERVER_PATH/

# Ejecutar deployment en el servidor
echo "🔄 Ejecutando deployment en el servidor..."
ssh $SERVER_USER@$SERVER_HOST << EOF
    cd $SERVER_PATH

    # Cargar nueva imagen
    docker load < $APP_NAME.tar.gz

    # Hacer backup de la versión actual
    docker tag $APP_NAME:latest $APP_NAME:backup 2>/dev/null || true

    # Detener contenedores existentes
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

    # Iniciar nuevos contenedores
    docker-compose -f docker-compose.prod.yml up -d

    # Verificar que la aplicación esté funcionando
    echo "⏳ Esperando que la aplicación inicie..."
    sleep 15

    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Aplicación funcionando correctamente!"
    else
        echo "❌ Error: La aplicación no responde"
        exit 1
    fi

    # Limpiar archivos temporales
    rm $APP_NAME.tar.gz

    # Limpiar imágenes viejas
    docker image prune -f

    echo "🎉 Deployment completado exitosamente!"
EOF

# Limpiar archivo local
rm $APP_NAME.tar.gz

echo "✨ Deployment finalizado. Tu API está disponible en http://$SERVER_HOST"