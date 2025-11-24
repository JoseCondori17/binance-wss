# Binance WebSocket ETL Project

## Introducción

Sistema ETL de alto rendimiento para análisis de mercado de criptomonedas que extrae datos en tiempo real de Binance (klines y aggregate trades), los procesa con Polars y los almacena en MongoDB. Incluye una API REST con FastAPI para consulta de KPIs (volatilidad, volumen, presión compradora/vendedora) y un dashboard interactivo con Streamlit para visualización de datos. La orquestación se realiza con Apache Airflow mediante ejecuciones programadas cada hora, todo desplegado en una arquitectura de microservicios con Docker Compose.

## Link Drive con toda la info

https://drive.google.com/drive/folders/1j-weCSCoBJ3C5njp_TRPb9CYb4d_E_x3?usp=sharing

## Requisitos Previos

- Python 3.12 o 3.13
- Docker y Docker Compose
- Cuenta de Binance con API Key y Secret Key

## Configuración Inicial

### 1. Crear archivo de variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_API_SECRET_KEY=tu_secret_key_aqui
BINANCE_API_BASE_URL=https://api.binance.com/api
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=binance_data
MONGODB_COLLECTION_NAME=kline_with_aggtrades
```

**¿Por qué?** El proyecto usa `pydantic-settings` para cargar configuraciones desde variables de entorno. Estas son necesarias para:
- Conectarse a la API de Binance (API_KEY y SECRET_KEY)
- Conectarse a MongoDB (MONGODB_URI)
- Configurar nombres de base de datos y colecciones

### 2. Iniciar MongoDB con Docker Compose

```bash
docker-compose up -d
```

**¿Por qué?** El proyecto necesita MongoDB para almacenar los datos. Docker Compose levanta un contenedor de MongoDB en el puerto 27017 con persistencia de datos.

**Verificar que MongoDB está corriendo:**
```bash
docker ps
```
Deberías ver el contenedor `mongodb-binance` corriendo.

### 3. Crear entorno virtual (recomendado)

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows
```

**¿Por qué?** Aísla las dependencias del proyecto del sistema y evita conflictos con otros proyectos.

### 4. Instalar dependencias

```bash
pip install -e .
```

**¿Por qué?** Instala el proyecto y todas sus dependencias definidas en `pyproject.toml`:
- `polars`: Para procesamiento de datos
- `python-binance`: Cliente de Binance API
- `streamlit`: Para el dashboard
- `beanie`: ODM para MongoDB
- `pydantic-settings`: Para configuración
- `plotly`: Para visualizaciones
- `fastapi`: Framework para la API REST
- `uvicorn`: Servidor ASGI para FastAPI

**Nota:** Si necesitas Airflow, instala las dependencias opcionales:
```bash
pip install -e ".[airflow]"
```

## Ejecución del Proyecto

### Inicializar la base de datos

```bash
python -m src.binance_wss.main
```

**¿Por qué?** Este comando inicializa Beanie (ODM de MongoDB) y crea los índices necesarios en las colecciones. Debe ejecutarse una vez antes de usar el proyecto.

### Ejecutar la API REST (FastAPI)

```bash
python -m src.binance_wss.run_api
# o directamente:
uvicorn binance_wss.api:app --reload --host 0.0.0.0 --port 8000
```

**¿Por qué?** Inicia el servidor FastAPI en `http://localhost:8000` con endpoints CRUD para gestionar las velas.

**Documentación interactiva:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Endpoints disponibles:**
- `GET /klines` - Listar velas (con filtros: symbol, fechas, paginación)
- `POST /klines` - Crear una nueva vela
- `GET /klines/{id}` - Obtener una vela por ID
- `PUT /klines/{id}` - Actualizar una vela
- `DELETE /klines/{id}` - Eliminar una vela
- `GET /klines/stats/symbols` - Listar símbolos únicos
- `GET /klines/stats/count` - Contar velas con filtros

### Ejecutar el Dashboard (Streamlit)

```bash
streamlit run dashboard/app.py
```

**¿Por qué?** Inicia el servidor de Streamlit en `http://localhost:8501` para visualizar los datos almacenados en MongoDB.

### Ejecutar el ETL manualmente

Puedes ejecutar el flujo ETL directamente desde Python:

```python
from binance_wss.extract.binance_client import extract_all
from binance_wss.transform.kline_processor import transform_merge
from binance_wss.load.mongo_loader import load_to_mongo
import asyncio

# Extraer datos
data = extract_all()

# Transformar datos
transformed_data = transform_merge(data)

# Cargar a MongoDB
asyncio.run(load_to_mongo(transformed_data))
```

### Ejecutar con Airflow (opcional)

Si tienes Airflow configurado:

```bash
# Iniciar Airflow (depende de tu configuración)
airflow standalone
```

El DAG `binance_klines_to_mongo` se ejecutará cada hora automáticamente.

## Comandos Útiles

### Ver logs de MongoDB
```bash
docker logs mongodb-binance
```

### Detener MongoDB
```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ elimina los datos)
```bash
docker-compose down -v
```

### Verificar conexión a MongoDB
```bash
docker exec -it mongodb-binance mongosh
```

## Estructura del Proyecto

```
binance-wss/
├── src/binance_wss/
│   ├── config/          # Configuración y settings
│   ├── extract/         # Extracción de datos de Binance
│   ├── transform/       # Transformación de datos
│   ├── load/            # Carga a MongoDB
│   ├── kpis/            # Indicadores y KPIs
│   ├── models/          # Modelos de Beanie (Kline, AggTrade)
│   ├── api.py           # API REST con FastAPI
│   ├── run_api.py       # Script para ejecutar la API
│   ├── run_etl_once.py  # Script para ejecutar ETL una vez
│   └── main.py          # Inicialización de BD
├── dashboard/           # Dashboard Streamlit
├── airflow-local/       # DAGs de Airflow
├── notebooks/           # Jupyter notebooks
└── docker-compose.yml   # Configuración de MongoDB
```

## Solución de Problemas

### Error: "Settings validation error"
- Verifica que el archivo `.env` existe y tiene todas las variables requeridas
- Asegúrate de que el archivo está en la raíz del proyecto

### Error: "Connection refused" a MongoDB
- Verifica que MongoDB está corriendo: `docker ps`
- Verifica que el puerto 27017 no está en uso por otro proceso

### Error: "Module not found"
- Asegúrate de haber instalado las dependencias: `pip install -e .`
- Verifica que estás en el entorno virtual correcto

