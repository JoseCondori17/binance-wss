from typing import Dict, List, Any
from datetime import datetime
from beanie import PydanticObjectId
from ..models.mongo_models import Kline


class KPIService:
    """Servicio para calcular KPIs de trading de criptomonedas"""

    @staticmethod
    async def calcular_volatilidad(
        symbol: str = None,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None
    ) -> Dict[str, Any]:
        """
        Calcula la volatilidad del mercado basándose en la variación de precios.
        
        Retorna:
        - Datos globales: promedio de volatilidad, unidad
        - Datos por símbolo: volatilidad promedio, máxima, precios extremos, número de registros
        """
        query = {}
        
        if symbol:
            query["symbol"] = symbol
        if fecha_inicio:
            query["open_time"] = {"$gte": fecha_inicio}
        if fecha_fin:
            if "open_time" in query:
                query["open_time"]["$lte"] = fecha_fin
            else:
                query["open_time"] = {"$lte": fecha_fin}

        klines = await Kline.find(query).to_list()
        
        if not klines:
            return {
                "datos_globales": {
                    "valor_global": 0.0,
                    "unidad": "porcentaje"
                },
                "datos_por_simbolo": []
            }

        # Agrupar por símbolo
        agrupado = {}
        for kline in klines:
            sym = kline.symbol
            if sym not in agrupado:
                agrupado[sym] = []
            
            # Calcular volatilidad de la vela
            volatilidad = ((kline.high_price - kline.low_price) / kline.low_price) * 100 if kline.low_price > 0 else 0
            
            agrupado[sym].append({
                "volatilidad": volatilidad,
                "high": kline.high_price,
                "low": kline.low_price
            })

        # Calcular métricas por símbolo
        datos_por_simbolo = []
        volatilidades_totales = []
        
        for sym, data in agrupado.items():
            volatilidades = [d["volatilidad"] for d in data]
            precios_altos = [d["high"] for d in data]
            precios_bajos = [d["low"] for d in data]
            
            volatilidad_promedio = sum(volatilidades) / len(volatilidades) if volatilidades else 0
            volatilidad_maxima = max(volatilidades) if volatilidades else 0
            
            volatilidades_totales.extend(volatilidades)
            
            datos_por_simbolo.append({
                "symbol": sym,
                "volatilidad_promedio": round(volatilidad_promedio, 4),
                "volatilidad_maxima": round(volatilidad_maxima, 4),
                "precio_max": round(max(precios_altos), 2) if precios_altos else 0,
                "precio_min": round(min(precios_bajos), 2) if precios_bajos else 0,
                "num_registros": len(data)
            })

        # Calcular valor global
        valor_global = sum(volatilidades_totales) / len(volatilidades_totales) if volatilidades_totales else 0

        return {
            "datos_globales": {
                "valor_global": round(valor_global, 4),
                "unidad": "porcentaje"
            },
            "datos_por_simbolo": sorted(datos_por_simbolo, key=lambda x: x["volatilidad_promedio"], reverse=True)
        }

    @staticmethod
    async def calcular_volumen_trading(
        symbol: str = None,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None
    ) -> Dict[str, Any]:
        """
        Calcula el volumen de trading del mercado.
        
        Retorna:
        - Datos globales: volumen total en BTC y USDT, trades totales
        - Datos por símbolo: volúmenes, número de trades, promedios
        """
        query = {}
        
        if symbol:
            query["symbol"] = symbol
        if fecha_inicio:
            query["open_time"] = {"$gte": fecha_inicio}
        if fecha_fin:
            if "open_time" in query:
                query["open_time"]["$lte"] = fecha_fin
            else:
                query["open_time"] = {"$lte": fecha_fin}

        klines = await Kline.find(query).to_list()
        
        if not klines:
            return {
                "datos_globales": {
                    "valor_global_btc": 0.0,
                    "valor_global_usdt": 0.0,
                    "trades_totales": 0
                },
                "datos_por_simbolo": []
            }

        # Agrupar por símbolo
        agrupado = {}
        for kline in klines:
            sym = kline.symbol
            if sym not in agrupado:
                agrupado[sym] = {
                    "volumen_btc": 0.0,
                    "volumen_usdt": 0.0,
                    "num_trades": 0,
                    "num_periodos": 0
                }
            
            agrupado[sym]["volumen_btc"] += kline.volume
            agrupado[sym]["volumen_usdt"] += kline.quote_asset_volume
            agrupado[sym]["num_trades"] += kline.number_of_trades
            agrupado[sym]["num_periodos"] += 1

        # Calcular métricas
        datos_por_simbolo = []
        total_btc = 0.0
        total_usdt = 0.0
        total_trades = 0
        
        for sym, data in agrupado.items():
            total_btc += data["volumen_btc"]
            total_usdt += data["volumen_usdt"]
            total_trades += data["num_trades"]
            
            volumen_promedio = data["volumen_btc"] / data["num_periodos"] if data["num_periodos"] > 0 else 0
            usdt_por_trade = data["volumen_usdt"] / data["num_trades"] if data["num_trades"] > 0 else 0
            
            datos_por_simbolo.append({
                "symbol": sym,
                "volumen_btc": round(data["volumen_btc"], 8),
                "volumen_usdt": round(data["volumen_usdt"], 2),
                "num_trades": data["num_trades"],
                "volumen_promedio_por_periodo": round(volumen_promedio, 8),
                "usdt_por_trade": round(usdt_por_trade, 2)
            })

        return {
            "datos_globales": {
                "valor_global_btc": round(total_btc, 8),
                "valor_global_usdt": round(total_usdt, 2),
                "trades_totales": total_trades
            },
            "datos_por_simbolo": sorted(datos_por_simbolo, key=lambda x: x["volumen_usdt"], reverse=True)
        }

    @staticmethod
    async def calcular_presion_compradora_vendedora(
        symbol: str = None,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None
    ) -> Dict[str, Any]:
        """
        Calcula la presión compradora vs vendedora basándose en taker buy volume.
        
        Retorna:
        - Datos globales: porcentaje de presión compradora, sentimiento global
        - Datos por símbolo: presiones, sentimiento, volúmenes exactos
        """
        query = {}
        
        if symbol:
            query["symbol"] = symbol
        if fecha_inicio:
            query["open_time"] = {"$gte": fecha_inicio}
        if fecha_fin:
            if "open_time" in query:
                query["open_time"]["$lte"] = fecha_fin
            else:
                query["open_time"] = {"$lte": fecha_fin}

        klines = await Kline.find(query).to_list()
        
        if not klines:
            return {
                "datos_globales": {
                    "valor_global_pct": 0.0,
                    "sentimiento_global": "NEUTRAL"
                },
                "datos_por_simbolo": []
            }

        # Agrupar por símbolo
        agrupado = {}
        for kline in klines:
            sym = kline.symbol
            if sym not in agrupado:
                agrupado[sym] = {
                    "volumen_compradores": 0.0,
                    "volumen_vendedores": 0.0,
                    "volumen_total": 0.0
                }
            
            vol_compradores = kline.taker_buy_base_asset_volume
            vol_total = kline.volume
            vol_vendedores = vol_total - vol_compradores
            
            agrupado[sym]["volumen_compradores"] += vol_compradores
            agrupado[sym]["volumen_vendedores"] += vol_vendedores
            agrupado[sym]["volumen_total"] += vol_total

        # Calcular métricas
        datos_por_simbolo = []
        volumen_compradores_global = 0.0
        volumen_total_global = 0.0
        
        for sym, data in agrupado.items():
            volumen_compradores_global += data["volumen_compradores"]
            volumen_total_global += data["volumen_total"]
            
            presion_compradora = (data["volumen_compradores"] / data["volumen_total"] * 100) if data["volumen_total"] > 0 else 50.0
            presion_vendedora = 100 - presion_compradora
            
            # Determinar sentimiento
            if presion_compradora > 55:
                sentimiento = "ALCISTA"
            elif presion_compradora < 45:
                sentimiento = "BAJISTA"
            else:
                sentimiento = "NEUTRAL"
            
            datos_por_simbolo.append({
                "symbol": sym,
                "presion_compradora": round(presion_compradora, 2),
                "presion_vendedora": round(presion_vendedora, 2),
                "sentimiento": sentimiento,
                "volumen_compradores": round(data["volumen_compradores"], 8),
                "volumen_vendedores": round(data["volumen_vendedores"], 8)
            })

        # Calcular datos globales
        valor_global_pct = (volumen_compradores_global / volumen_total_global * 100) if volumen_total_global > 0 else 50.0
        
        if valor_global_pct > 55:
            sentimiento_global = "ALCISTA"
        elif valor_global_pct < 45:
            sentimiento_global = "BAJISTA"
        else:
            sentimiento_global = "NEUTRAL"

        return {
            "datos_globales": {
                "valor_global_pct": round(valor_global_pct, 2),
                "sentimiento_global": sentimiento_global
            },
            "datos_por_simbolo": sorted(datos_por_simbolo, key=lambda x: x["presion_compradora"], reverse=True)
        }

    @staticmethod
    async def calcular_aggtrades_stats(
        symbol: str = None,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None
    ) -> Dict[str, Any]:
        """
        Estadísticas adicionales basadas en aggtrades para enriquecer el dashboard.
        
        Retorna estadísticas de trades individuales por símbolo.
        """
        query = {}
        
        if symbol:
            query["symbol"] = symbol
        if fecha_inicio:
            query["open_time"] = {"$gte": fecha_inicio}
        if fecha_fin:
            if "open_time" in query:
                query["open_time"]["$lte"] = fecha_fin
            else:
                query["open_time"] = {"$lte": fecha_fin}

        klines = await Kline.find(query).to_list()
        
        if not klines:
            return {
                "datos_por_simbolo": []
            }

        # Agrupar por símbolo
        agrupado = {}
        for kline in klines:
            sym = kline.symbol
            if sym not in agrupado:
                agrupado[sym] = {
                    "total_aggtrades": 0,
                    "trades_compradores": 0,
                    "trades_vendedores": 0,
                    "cantidad_promedio": 0.0,
                    "total_cantidad": 0.0
                }
            
            for aggtrade in kline.aggtrades:
                agrupado[sym]["total_aggtrades"] += 1
                agrupado[sym]["total_cantidad"] += aggtrade.quantity
                
                if not aggtrade.is_buyer_maker:
                    agrupado[sym]["trades_compradores"] += 1
                else:
                    agrupado[sym]["trades_vendedores"] += 1

        # Calcular métricas
        datos_por_simbolo = []
        
        for sym, data in agrupado.items():
            cantidad_promedio = data["total_cantidad"] / data["total_aggtrades"] if data["total_aggtrades"] > 0 else 0
            pct_trades_compradores = (data["trades_compradores"] / data["total_aggtrades"] * 100) if data["total_aggtrades"] > 0 else 0
            
            datos_por_simbolo.append({
                "symbol": sym,
                "total_aggtrades": data["total_aggtrades"],
                "trades_compradores": data["trades_compradores"],
                "trades_vendedores": data["trades_vendedores"],
                "pct_trades_compradores": round(pct_trades_compradores, 2),
                "cantidad_promedio_trade": round(cantidad_promedio, 8)
            })

        return {
            "datos_por_simbolo": sorted(datos_por_simbolo, key=lambda x: x["total_aggtrades"], reverse=True)
        }
