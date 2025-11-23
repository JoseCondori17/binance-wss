# Ejemplos de Uso de la API REST

## Iniciar la API

```bash
# Opción 1: Usando el script
python -m src.binance_wss.run_api

# Opción 2: Directamente con uvicorn
uvicorn binance_wss.api:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

## Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplos de Uso con cURL

### 1. Listar todas las velas (GET /klines)

```bash
# Obtener las últimas 100 velas
curl http://localhost:8000/klines

# Filtrar por símbolo
curl "http://localhost:8000/klines?symbol=BTCUSDT"

# Filtrar por rango de fechas
curl "http://localhost:8000/klines?start_date=2025-01-01T00:00:00&end_date=2025-01-31T23:59:59"

# Combinar filtros con paginación
curl "http://localhost:8000/klines?symbol=BTCUSDT&limit=50&skip=0&sort_by=volume&sort_order=desc"
```

### 2. Crear una nueva vela (POST /klines)

```bash
curl -X POST "http://localhost:8000/klines" \
  -H "Content-Type: application/json" \
  -d '{
    "open_time": "2025-01-20T12:00:00",
    "close_time": "2025-01-20T12:00:59",
    "symbol": "BTCUSDT",
    "interval": "1m",
    "open_price": 86000.0,
    "close_price": 86100.0,
    "high_price": 86200.0,
    "low_price": 85900.0,
    "volume": 10.5,
    "quote_asset_volume": 903000.0,
    "number_of_trades": 1500,
    "taker_buy_base_asset_volume": 5.2,
    "taker_buy_quote_asset_volume": 447360.0,
    "aggtrades": []
  }'
```

### 3. Obtener una vela por ID (GET /klines/{id})

```bash
curl "http://localhost:8000/klines/507f1f77bcf86cd799439011"
```

### 4. Actualizar una vela (PUT /klines/{id})

```bash
curl -X PUT "http://localhost:8000/klines/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json" \
  -d '{
    "volume": 12.5,
    "number_of_trades": 1800
  }'
```

### 5. Eliminar una vela (DELETE /klines/{id})

```bash
curl -X DELETE "http://localhost:8000/klines/507f1f77bcf86cd799439011"
```

### 6. Obtener estadísticas

```bash
# Listar todos los símbolos únicos
curl "http://localhost:8000/klines/stats/symbols"

# Contar velas con filtros
curl "http://localhost:8000/klines/stats/count?symbol=BTCUSDT"
curl "http://localhost:8000/klines/stats/count?start_date=2025-01-01T00:00:00&end_date=2025-01-31T23:59:59"
```

## Ejemplos con Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Listar velas
response = requests.get(f"{BASE_URL}/klines", params={
    "symbol": "BTCUSDT",
    "limit": 10,
    "sort_by": "open_time",
    "sort_order": "desc"
})
klines = response.json()
print(f"Total de velas: {len(klines)}")

# 2. Crear una nueva vela
new_kline = {
    "open_time": "2025-01-20T12:00:00",
    "close_time": "2025-01-20T12:00:59",
    "symbol": "BTCUSDT",
    "interval": "1m",
    "open_price": 86000.0,
    "close_price": 86100.0,
    "high_price": 86200.0,
    "low_price": 85900.0,
    "volume": 10.5,
    "quote_asset_volume": 903000.0,
    "number_of_trades": 1500,
    "taker_buy_base_asset_volume": 5.2,
    "taker_buy_quote_asset_volume": 447360.0,
    "aggtrades": []
}
response = requests.post(f"{BASE_URL}/klines", json=new_kline)
created_kline = response.json()
print(f"Vela creada con ID: {created_kline['id']}")

# 3. Obtener una vela por ID
kline_id = created_kline['id']
response = requests.get(f"{BASE_URL}/klines/{kline_id}")
kline = response.json()
print(f"Vela obtenida: {kline['symbol']} - {kline['open_time']}")

# 4. Actualizar una vela
update_data = {"volume": 15.0}
response = requests.put(f"{BASE_URL}/klines/{kline_id}", json=update_data)
updated_kline = response.json()
print(f"Volumen actualizado: {updated_kline['volume']}")

# 5. Eliminar una vela
response = requests.delete(f"{BASE_URL}/klines/{kline_id}")
print(response.json())

# 6. Obtener estadísticas
response = requests.get(f"{BASE_URL}/klines/stats/symbols")
symbols = response.json()
print(f"Símbolos disponibles: {symbols['symbols']}")

response = requests.get(f"{BASE_URL}/klines/stats/count", params={"symbol": "BTCUSDT"})
count = response.json()
print(f"Total de velas BTCUSDT: {count['count']}")
```

## Ejemplos con JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// 1. Listar velas
async function listKlines() {
  const response = await fetch(`${BASE_URL}/klines?symbol=BTCUSDT&limit=10`);
  const klines = await response.json();
  console.log("Velas:", klines);
}

// 2. Crear una vela
async function createKline() {
  const newKline = {
    open_time: "2025-01-20T12:00:00",
    close_time: "2025-01-20T12:00:59",
    symbol: "BTCUSDT",
    interval: "1m",
    open_price: 86000.0,
    close_price: 86100.0,
    high_price: 86200.0,
    low_price: 85900.0,
    volume: 10.5,
    quote_asset_volume: 903000.0,
    number_of_trades: 1500,
    taker_buy_base_asset_volume: 5.2,
    taker_buy_quote_asset_volume: 447360.0,
    aggtrades: []
  };
  
  const response = await fetch(`${BASE_URL}/klines`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newKline)
  });
  const created = await response.json();
  console.log("Vela creada:", created);
  return created.id;
}

// 3. Obtener una vela por ID
async function getKline(id) {
  const response = await fetch(`${BASE_URL}/klines/${id}`);
  const kline = await response.json();
  console.log("Vela:", kline);
}

// 4. Actualizar una vela
async function updateKline(id) {
  const updateData = { volume: 15.0 };
  const response = await fetch(`${BASE_URL}/klines/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updateData)
  });
  const updated = await response.json();
  console.log("Vela actualizada:", updated);
}

// 5. Eliminar una vela
async function deleteKline(id) {
  const response = await fetch(`${BASE_URL}/klines/${id}`, {
    method: "DELETE"
  });
  const result = await response.json();
  console.log("Resultado:", result);
}
```

## Filtros Disponibles en GET /klines

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `symbol` | string | Filtrar por símbolo | `BTCUSDT`, `ETHUSDT` |
| `start_date` | datetime | Fecha de inicio (open_time >= start_date) | `2025-01-01T00:00:00` |
| `end_date` | datetime | Fecha de fin (open_time <= end_date) | `2025-01-31T23:59:59` |
| `limit` | int | Número máximo de resultados (1-1000) | `100` (default) |
| `skip` | int | Número de resultados a saltar (paginación) | `0` (default) |
| `sort_by` | string | Campo por el cual ordenar | `open_time`, `volume`, `symbol` |
| `sort_order` | string | Orden: `asc` o `desc` | `desc` (default) |

## Notas Importantes

1. **Fechas**: Usa formato ISO 8601: `YYYY-MM-DDTHH:MM:SS` o `YYYY-MM-DDTHH:MM:SSZ`
2. **IDs**: Los IDs de MongoDB son ObjectId, úsalos como strings
3. **Paginación**: Usa `skip` y `limit` para paginar resultados grandes
4. **CORS**: La API tiene CORS habilitado para todos los orígenes (cambiar en producción)

