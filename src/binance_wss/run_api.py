"""
Script para ejecutar la API REST de Binance Klines.
pip install polars motor beanie python-binance pydantic-settings fastapi "uvicorn[standard]"
python -m src.binance_wss.run_api
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "binance_wss.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )

