import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "binance_wss.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )