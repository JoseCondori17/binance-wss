from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from ..services.kpi_service import KPIService

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("/volatilidad")
async def get_volatilidad(
    symbol: Optional[str] = Query(None, description="Símbolo del par de trading (ej: BTCUSDT)"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio del periodo"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin del periodo")
):
    """
    KPI: Volatilidad del Mercado
    
    Retorna la volatilidad basada en la variación de precios high-low.
    
    Respuesta:
    - datos_globales: Promedio de volatilidad global en porcentaje
    - datos_por_simbolo: Métricas detalladas por cada símbolo
    """
    return await KPIService.calcular_volatilidad(symbol, fecha_inicio, fecha_fin)


@router.get("/volumen")
async def get_volumen_trading(
    symbol: Optional[str] = Query(None, description="Símbolo del par de trading (ej: BTCUSDT)"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio del periodo"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin del periodo")
):
    """
    KPI: Volumen de Trading
    
    Retorna el volumen de trading en BTC y USDT, junto con número de trades.
    
    Respuesta:
    - datos_globales: Volumen total BTC, USDT y número de trades
    - datos_por_simbolo: Volúmenes y estadísticas por símbolo
    """
    return await KPIService.calcular_volumen_trading(symbol, fecha_inicio, fecha_fin)


@router.get("/presion")
async def get_presion_compradora_vendedora(
    symbol: Optional[str] = Query(None, description="Símbolo del par de trading (ej: BTCUSDT)"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio del periodo"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin del periodo")
):
    """
    KPI: Presión Compradora vs Vendedora
    
    Retorna la presión de compra/venta basada en taker buy volume.
    
    Respuesta:
    - datos_globales: Porcentaje global de presión compradora y sentimiento del mercado
    - datos_por_simbolo: Presión y sentimiento por cada símbolo
    """
    return await KPIService.calcular_presion_compradora_vendedora(symbol, fecha_inicio, fecha_fin)


@router.get("/aggtrades-stats")
async def get_aggtrades_stats(
    symbol: Optional[str] = Query(None, description="Símbolo del par de trading (ej: BTCUSDT)"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio del periodo"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin del periodo")
):
    """
    Estadísticas de Aggregate Trades
    
    Retorna estadísticas detalladas de los trades agregados.
    
    Respuesta:
    - datos_por_simbolo: Total de trades, distribución compradores/vendedores, cantidades promedio
    """
    return await KPIService.calcular_aggtrades_stats(symbol, fecha_inicio, fecha_fin)


@router.get("/resumen")
async def get_resumen_completo(
    symbol: Optional[str] = Query(None, description="Símbolo del par de trading (ej: BTCUSDT)"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio del periodo"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin del periodo")
):
    """
    Resumen Completo de Todos los KPIs
    
    Retorna todos los KPIs en una sola llamada para optimizar el dashboard.
    
    Respuesta:
    - volatilidad: Datos de volatilidad del mercado
    - volumen: Datos de volumen de trading
    - presion: Datos de presión compradora/vendedora
    - aggtrades: Estadísticas de trades agregados
    """
    volatilidad = await KPIService.calcular_volatilidad(symbol, fecha_inicio, fecha_fin)
    volumen = await KPIService.calcular_volumen_trading(symbol, fecha_inicio, fecha_fin)
    presion = await KPIService.calcular_presion_compradora_vendedora(symbol, fecha_inicio, fecha_fin)
    aggtrades = await KPIService.calcular_aggtrades_stats(symbol, fecha_inicio, fecha_fin)
    
    return {
        "volatilidad": volatilidad,
        "volumen": volumen,
        "presion": presion,
        "aggtrades": aggtrades
    }
