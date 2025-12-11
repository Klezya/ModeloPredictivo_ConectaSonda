# ConectaSonda - Sistema Predictivo de Fallas

## Descripcion del Proyecto

ConectaSonda es un sistema de monitoreo y prediccion de fallas para equipos de borde (torniquetes y maquinas Transbank) en estaciones de transporte. El sistema permite:

- Visualizar el estado operativo de equipos en tiempo real
- Detectar anomalias de uso que indican degradacion del equipo
- Predecir fallas con hasta 7 dias de anticipacion mediante modelos de Machine Learning
- Programar mantenimientos preventivos y correctivos
- Generar reportes de operacion

## Arquitectura

El proyecto esta compuesto por:

- **Backend**: API REST desarrollada con FastAPI (Python 3.12), conectada a Supabase como base de datos
- **Frontend**: Aplicacion SPA desarrollada con Vue.js 3 y TypeScript, empaquetada con Vite
- **Infraestructura**: Contenedores Docker orquestados con Docker Compose, desplegados en AWS EC2

## Requisitos Previos

- Docker y Docker Compose
- Node.js 20.19.0+ o 22.12.0+ (para desarrollo local del frontend)
- Python 3.12+ (para desarrollo local del backend)
- Cuenta en Supabase con una tabla `equipos_borde` configurada

## Variables de Entorno

### Backend

Crear archivo `backend/.env`:

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-api-key
```

### Frontend

Crear archivo `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
VITE_ADMIN_USER=admin_user
VITE_ADMIN_PASSWORD=admin_password
```

## Instalacion Local

### Backend

```sh
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```sh
cd frontend
npm install
npm run dev
```

El frontend estara disponible en `http://localhost:5173` y el backend en `http://localhost:8000`.

## Despliegue con Docker

### Construccion y ejecucion

```sh
docker compose up --build -d
```

Esto levantara:

- Backend en `http://localhost:8001`
- Frontend en `http://localhost:3000`

### Detener los servicios

```sh
docker compose down
```

### Ver logs

```sh
docker compose logs -f
```

## Despliegue en Produccion (AWS EC2)

El proyecto incluye un workflow de GitHub Actions que automatiza el despliegue a EC2.

### Configuracion de Secrets en GitHub

Agregar los siguientes secrets en el repositorio:

- `EC2_SSH_KEY`: Clave privada SSH para acceder a la instancia EC2
- `VITE_API_URL`: URL publica del backend (ejemplo: `http://tu-dominio:8001`)
- `VITE_ADMIN_USER`: Usuario de administracion
- `VITE_ADMIN_PASSWORD`: Contrasena de administracion

### Proceso de Despliegue

1. Hacer push a la rama `main`
2. El workflow ejecutara pruebas automaticas
3. Si las pruebas pasan, sincronizara el codigo con EC2
4. Reconstruira y reiniciara los contenedores Docker
5. Ejecutara una verificacion de salud del sistema

### Despliegue Manual

Tambien es posible ejecutar el despliegue manualmente desde la pestana Actions del repositorio.

## Estructura del Proyecto

```
ModeloPredictivo_ConectaSonda/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── requirements.txt     # Dependencias Python
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/           # Vistas Vue
│   │   ├── services/        # Servicios API
│   │   └── router/          # Configuracion de rutas
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/
    └── deploy.yml           # Pipeline CI/CD
```

## Endpoints de la API

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /api/health | Verificacion de salud del sistema |
| GET | /api/metrics | Metricas generales del dashboard |
| GET | /api/equipments | Lista de equipos |
| GET | /api/equipments/{id} | Detalle de un equipo |
| GET | /api/failures | Historial de fallas |
| POST | /api/predict/{id} | Ejecutar prediccion de falla |
| POST | /api/maintenance | Programar mantenimiento |
| GET | /api/reports/generate | Generar reporte |

## Credenciales por Defecto

Para el entorno de desarrollo:

- Usuario: `admin_user`
- Contrasena: `admin_password`

Estas credenciales deben cambiarse en produccion mediante las variables de entorno.

## Licencia

Este proyecto es de uso interno para ConectaSonda.
