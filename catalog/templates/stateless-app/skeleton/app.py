import os
import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "local")


@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Hello from ${{ values.component_id }}!", "env": APP_ENV}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
def readiness_check():
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
