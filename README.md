# 🚀 FastAPI con Docker y GitHub Actions - Guía Completa

## 📁 Estructura del Proyecto

```
fastapi-project/
├── main.py                     # Aplicación FastAPI principal
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Para desarrollo local
├── docker-compose.prod.yml     # Para producción
├── nginx.conf                  # Configuración Nginx
├── deploy.sh                   # Script deployment manual
├── tests/
│   └── test_main.py           # Tests unitarios
└── .github/
    └── workflows/
        └── deploy.yml         # GitHub Actions workflow
```

## 🛠️ Configuración Inicial

### 1. Crear el proyecto

```bash
mkdir fastapi-project
cd fastapi-project
```

### 2. Crear archivos del proyecto
Copia todos los archivos de código proporcionados en los artifacts.

### 3. Configurar Git y GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repositorio.git
git push -u origin main
```

## 🔐 Configuración de Secrets en GitHub

Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions

Agregar estos secrets:

- `HOST`: IP o dominio de tu servidor (ej: `192.168.1.100`)
- `USERNAME`: Usuario SSH (ej: `ubuntu`)
- `PRIVATE_KEY`: Clave privada SSH (contenido del archivo `~/.ssh/id_rsa`)
- `PORT`: Puerto SSH (generalmente `22`)

## 🖥️ Preparación del Servidor

### 1. Instalar Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Instalar Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Crear directorio para la aplicación

```bash
sudo mkdir -p /opt/fastapi-app
sudo chown $USER:$USER /opt/fastapi-app
```

### 4. Configurar firewall

```bash
# Ubuntu/Debian con ufw
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS (opcional)
sudo ufw enable
```

## 🧪 Desarrollo Local

### 1. Desarrollo sin Docker

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Desarrollo con Docker

```bash
# Construir y ejecutar
docker-compose up --build

# Solo ejecutar (sin rebuild)
docker-compose up

# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### 3. Ejecutar tests

```bash
# Sin Docker
pip install pytest httpx
pytest tests/ -v

# Con Docker
docker run --rm fastapi-app pytest tests/ -v
```

## 🚀 Deployment

### Opción 1: GitHub Actions (Automático)

1. Configura los secrets en GitHub
2. Haz push a la rama `main`
3. GitHub Actions se ejecutará automáticamente

### Opción 2: Script Manual

```bash
# Hacer ejecutable el script
chmod +x deploy.sh

# Editar variables en deploy.sh
nano deploy.sh

# Ejecutar deployment
./deploy.sh
```

### Opción 3: Manual paso a paso

```bash
# En tu máquina local
docker build -t fastapi-app:latest .
docker save fastapi-app:latest | gzip > fastapi-app.tar.gz
scp fastapi-app.tar.gz usuario@servidor:/opt/fastapi-app/
scp docker-compose.prod.yml usuario@servidor:/opt/fastapi-app/

# En el servidor
ssh usuario@servidor
cd /opt/fastapi-app
docker load < fastapi-app.tar.gz
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Verificación y Monitoreo

### Verificar que funciona

```bash
curl http://tu-servidor/health
curl http://tu-servidor/
curl http://tu-servidor/items
```

### Ver logs

```bash
# En el servidor
docker-compose -f docker-compose.prod.yml logs -f

# Ver logs específicos
docker logs fastapi-api
docker logs fastapi-nginx
```

### Comandos útiles

```bash
# Ver contenedores activos
docker ps

# Ver uso de recursos
docker stats

# Entrar a un contenedor
docker exec -it fastapi-api bash

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart
```

## 🔧 Troubleshooting

### Problemas comunes:

1. **Puerto ocupado**: Cambiar puerto en docker-compose
2. **Permisos SSH**: Verificar que la clave privada tenga permisos 600
3. **Firewall**: Asegurar que los puertos estén abiertos
4. **Docker daemon**: `sudo systemctl start docker`
5. **Memoria insuficiente**: Verificar recursos del servidor

### Rollback rápido:

```bash
docker tag fastapi-app:backup fastapi-app:latest
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 URLs de la API

- **Documentación**: http://tu-servidor/docs
- **ReDoc**: http://tu-servidor/redoc
- **Health Check**: http://tu-servidor/health
- **API Base**: http://tu-servidor/

## 🔒 Mejoras de Seguridad (Opcionales)

1. **SSL/HTTPS**: Usar Let's Encrypt con Certbot
2. **Rate Limiting**: Implementar en Nginx
3. **Autenticación**: JWT tokens
4. **Monitoring**: Prometheus + Grafana
5. **Backup**: Scripts automáticos de backup

## 📝 Notas Importantes

- El workflow de GitHub Actions se ejecuta solo en push a `main`
- Los tests deben pasar antes del deployment
- Se hace backup automático de la versión anterior
- Los logs están disponibles con `docker-compose logs`
- La aplicación se reinicia automáticamente si falla