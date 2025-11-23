"""
API REST para gestionar Klines de Binance usando FastAPI y Beanie.
Endpoints CRUD completos con filtros avanzados.
"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from binance_wss.main import init_db
from binance_wss.models.mongo_models import Kline, AggTrade


# ---------- Modelos Pydantic para la API ----------
class AggTradeResponse(BaseModel):
    """Modelo de respuesta para AggTrade"""
    trade_id: int
    price: float
    quantity: float
    first_trade_id: int
    last_trade_id: int
    timestamp: datetime
    is_buyer_maker: bool
    is_best_match: bool


class KlineBase(BaseModel):
    """Modelo base para Kline"""
    open_time: datetime
    close_time: datetime
    symbol: str
    interval: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: float
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    aggtrades: List[AggTradeResponse] = []


class KlineCreate(KlineBase):
    """Modelo para crear una nueva Kline"""
    pass


class KlineUpdate(BaseModel):
    """Modelo para actualizar una Kline (todos los campos opcionales)"""
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    symbol: Optional[str] = None
    interval: Optional[str] = None
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[float] = None
    quote_asset_volume: Optional[float] = None
    number_of_trades: Optional[int] = None
    taker_buy_base_asset_volume: Optional[float] = None
    taker_buy_quote_asset_volume: Optional[float] = None
    aggtrades: Optional[List[AggTradeResponse]] = None


class KlineResponse(KlineBase):
    """Modelo de respuesta para Kline (incluye el ID)"""
    id: str

    class Config:
        from_attributes = True


# ---------- FastAPI App ----------
app = FastAPI(
    title="Binance Klines API",
    description="API REST para gestionar velas (klines) de Binance almacenadas en MongoDB",
    version="1.0.0"
)

# CORS middleware para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Event Handlers ----------
@app.on_event("startup")
async def startup_event():
    """Inicializa la conexión a MongoDB al iniciar la API"""
    await init_db()
    print("MongoDB conectado y Beanie inicializado")


@app.on_event("shutdown")
async def shutdown_event():
    """Cierra conexiones al apagar la API"""
    print(" Cerrando conexiones...")


# ---------- Helper Functions ----------
def kline_to_response(kline: Kline) -> KlineResponse:
    """Convierte un documento Kline de Beanie a KlineResponse"""
    return KlineResponse(
        id=str(kline.id),
        open_time=kline.open_time,
        close_time=kline.close_time,
        symbol=kline.symbol,
        interval=kline.interval,
        open_price=kline.open_price,
        close_price=kline.close_price,
        high_price=kline.high_price,
        low_price=kline.low_price,
        volume=kline.volume,
        quote_asset_volume=kline.quote_asset_volume,
        number_of_trades=kline.number_of_trades,
        taker_buy_base_asset_volume=kline.taker_buy_base_asset_volume,
        taker_buy_quote_asset_volume=kline.taker_buy_quote_asset_volume,
        aggtrades=[
            AggTradeResponse(
                trade_id=agg.trade_id,
                price=agg.price,
                quantity=agg.quantity,
                first_trade_id=agg.first_trade_id,
                last_trade_id=agg.last_trade_id,
                timestamp=agg.timestamp,
                is_buyer_maker=agg.is_buyer_maker,
                is_best_match=agg.is_best_match,
            )
            for agg in kline.aggtrades
        ]
    )


# ---------- Endpoints CRUD ----------

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Binance Klines API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "GET /klines": "Listar velas con filtros",
            "POST /klines": "Crear una nueva vela",
            "GET /klines/{id}": "Obtener una vela por ID",
            "PUT /klines/{id}": "Actualizar una vela",
            "DELETE /klines/{id}": "Eliminar una vela"
        }
    }


@app.post("/klines", response_model=KlineResponse, status_code=201, tags=["Klines"])
async def create_kline(kline: KlineCreate):
    """
    **POST /klines** - Crear una nueva vela
    
    Crea una nueva vela en la base de datos.
    """
    try:
        # Convertir AggTradeResponse a AggTrade
        aggtrades = [
            AggTrade(
                trade_id=agg.trade_id,
                price=agg.price,
                quantity=agg.quantity,
                first_trade_id=agg.first_trade_id,
                last_trade_id=agg.last_trade_id,
                timestamp=agg.timestamp,
                is_buyer_maker=agg.is_buyer_maker,
                is_best_match=agg.is_best_match,
            )
            for agg in kline.aggtrades
        ]
        
        new_kline = Kline(
            open_time=kline.open_time,
            close_time=kline.close_time,
            symbol=kline.symbol,
            interval=kline.interval,
            open_price=kline.open_price,
            close_price=kline.close_price,
            high_price=kline.high_price,
            low_price=kline.low_price,
            volume=kline.volume,
            quote_asset_volume=kline.quote_asset_volume,
            number_of_trades=kline.number_of_trades,
            taker_buy_base_asset_volume=kline.taker_buy_base_asset_volume,
            taker_buy_quote_asset_volume=kline.taker_buy_quote_asset_volume,
            aggtrades=aggtrades,
        )
        
        await new_kline.insert()
        return kline_to_response(new_kline)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear kline: {str(e)}")


@app.get("/klines", response_model=List[KlineResponse], tags=["Klines"])
async def list_klines(
    symbol: Optional[str] = Query(None, description="Filtrar por símbolo (ej: BTCUSDT)"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (open_time >= start_date)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (open_time <= end_date)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    skip: int = Query(0, ge=0, description="Número de resultados a saltar (paginación)"),
    sort_by: str = Query("open_time", description="Campo por el cual ordenar"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Orden: 'asc' o 'desc'")
):
    """
    **GET /klines** - Listar velas con filtros
    
    Obtiene una lista de velas con los siguientes filtros opcionales:
    - **symbol**: Filtrar por símbolo (ej: BTCUSDT, ETHUSDT)
    - **start_date**: Filtrar velas desde esta fecha (open_time >= start_date)
    - **end_date**: Filtrar velas hasta esta fecha (open_time <= end_date)
    - **limit**: Número máximo de resultados (1-1000, default: 100)
    - **skip**: Número de resultados a saltar para paginación (default: 0)
    - **sort_by**: Campo por el cual ordenar (default: open_time)
    - **sort_order**: Orden ascendente ('asc') o descendente ('desc', default)
    
    **Ejemplos:**
    - `/klines?symbol=BTCUSDT&limit=50`
    - `/klines?start_date=2025-01-01T00:00:00&end_date=2025-01-31T23:59:59`
    - `/klines?symbol=ETHUSDT&limit=10&skip=20&sort_by=volume&sort_order=desc`
    """
    try:
        # Construir query de filtrado
        query = {}
        
        if symbol:
            query["symbol"] = symbol
        
        if start_date or end_date:
            query["open_time"] = {}
            if start_date:
                query["open_time"]["$gte"] = start_date
            if end_date:
                query["open_time"]["$lte"] = end_date
        
        # Construir ordenamiento
        sort_direction = -1 if sort_order == "desc" else 1
        sort_field = sort_by if sort_by in [
            "open_time", "close_time", "open_price", "close_price",
            "high_price", "low_price", "volume", "symbol"
        ] else "open_time"
        
        # Ejecutar query con Beanie
        klines = await Kline.find(query).sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        
        return [kline_to_response(kline) for kline in klines]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener klines: {str(e)}")


@app.get("/klines/{kline_id}", response_model=KlineResponse, tags=["Klines"])
async def get_kline(kline_id: str):
    """
    **GET /klines/{id}** - Obtener una vela por ID
    
    Obtiene una vela específica usando su ID de MongoDB.
    """
    try:
        if not ObjectId.is_valid(kline_id):
            raise HTTPException(status_code=400, detail="ID inválido")
        
        kline = await Kline.get(kline_id)
        if not kline:
            raise HTTPException(status_code=404, detail="Kline no encontrada")
        
        return kline_to_response(kline)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener kline: {str(e)}")


@app.put("/klines/{kline_id}", response_model=KlineResponse, tags=["Klines"])
async def update_kline(kline_id: str, kline_update: KlineUpdate):
    """
    **PUT /klines/{id}** - Actualizar una vela
    
    Actualiza una vela existente. Solo los campos proporcionados serán actualizados.
    """
    try:
        if not ObjectId.is_valid(kline_id):
            raise HTTPException(status_code=400, detail="ID inválido")
        
        kline = await Kline.get(kline_id)
        if not kline:
            raise HTTPException(status_code=404, detail="Kline no encontrada")
        
        # Actualizar solo los campos proporcionados
        update_data = kline_update.model_dump(exclude_unset=True)
        
        if "aggtrades" in update_data:
            # Convertir AggTradeResponse a AggTrade
            update_data["aggtrades"] = [
                AggTrade(
                    trade_id=agg.trade_id,
                    price=agg.price,
                    quantity=agg.quantity,
                    first_trade_id=agg.first_trade_id,
                    last_trade_id=agg.last_trade_id,
                    timestamp=agg.timestamp,
                    is_buyer_maker=agg.is_buyer_maker,
                    is_best_match=agg.is_best_match,
                )
                for agg in kline_update.aggtrades
            ]
        
        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(kline, field, value)
        
        await kline.save()
        return kline_to_response(kline)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar kline: {str(e)}")


@app.delete("/klines/{kline_id}", tags=["Klines"])
async def delete_kline(kline_id: str):
    """
    **DELETE /klines/{id}** - Eliminar una vela
    
    Elimina una vela de la base de datos.
    """
    try:
        if not ObjectId.is_valid(kline_id):
            raise HTTPException(status_code=400, detail="ID inválido")
        
        kline = await Kline.get(kline_id)
        if not kline:
            raise HTTPException(status_code=404, detail="Kline no encontrada")
        
        await kline.delete()
        return {"detail": "Kline eliminada exitosamente", "id": kline_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar kline: {str(e)}")


# ---------- Endpoints adicionales útiles ----------

@app.get("/klines/stats/symbols", tags=["Stats"])
async def get_symbols():
    """
    **GET /klines/stats/symbols** - Obtener lista de símbolos únicos
    
    Retorna una lista de todos los símbolos únicos en la base de datos.
    """
    try:
        pipeline = [
            {"$group": {"_id": "$symbol"}},
            {"$sort": {"_id": 1}}
        ]
        symbols = await Kline.aggregate(pipeline).to_list()
        return {"symbols": [s["_id"] for s in symbols]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener símbolos: {str(e)}")


@app.get("/klines/stats/count", tags=["Stats"])
async def get_count(
    symbol: Optional[str] = Query(None, description="Filtrar por símbolo"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin")
):
    """
    **GET /klines/stats/count** - Contar velas
    
    Retorna el número total de velas que coinciden con los filtros.
    """
    try:
        query = {}
        if symbol:
            query["symbol"] = symbol
        if start_date or end_date:
            query["open_time"] = {}
            if start_date:
                query["open_time"]["$gte"] = start_date
            if end_date:
                query["open_time"]["$lte"] = end_date
        
        count = await Kline.find(query).count()
        return {"count": count, "filters": {"symbol": symbol, "start_date": start_date, "end_date": end_date}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contar klines: {str(e)}")
