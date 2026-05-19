#!/bin/bash

# Script de Despliegue Automatizado para Wynwood House
# Este script asume que ya existe el archivo .env y docker-compose.prod.yml

echo "🚀 Iniciando despliegue de Wynwood..."

# 1. Configurar Nginx
echo "⚙️ Configurando Nginx..."
sudo cp nginx_wynwood.conf /etc/nginx/sites-available/wynwood.jean-rivas.com
sudo ln -sf /etc/nginx/sites-available/wynwood.jean-rivas.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 2. Levantar Docker
echo "🐳 Levantando contenedores con Docker Compose..."
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 3. Migraciones y Estáticos
echo "📦 Ejecutando migraciones..."
docker exec wynwood-backend python manage.py migrate --noinput

echo "✨ Recolectando archivos estáticos..."
docker exec wynwood-backend python manage.py collectstatic --noinput

# 4. SSL con Certbot
echo "🔒 ¿Deseas configurar SSL ahora? (Requiere que el DNS ya apunte al servidor)"
echo "Si es así, ejecuta manualmente: sudo certbot --nginx -d wynwood.jean-rivas.com"

echo "✅ ¡Despliegue completado con éxito!"
echo "Accede a: http://wynwood.jean-rivas.com (o https si ya configuraste SSL)"
