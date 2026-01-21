import os
import time
import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "local")
DATA_PATH = os.getenv("DATA_PATH", "/data")
FILE_PATH = os.path.join(DATA_PATH, "access_log.txt")

@app.get("/")
def read_root():
    # Persist access time
    try:
        with open(FILE_PATH, "a") as f:
            f.write(f"Accessed at {time.time()}\n")
        
        # Read persistence count
        with open(FILE_PATH, "r") as f:
            count = len(f.readlines())
            
        msg = f"Hello from Stateful App! I have been accessed {count} times (persisted)."
    except Exception as e:
        msg = f"Error accessing storage at {DATA_PATH}: {str(e)}"
        
    return {"message": msg, "env": APP_ENV, "persistence_path": DATA_PATH}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ready")
def readiness_check():
    return {"status": "ready"}

if __name__ == "__main__":
    import uvicorn
    # Ensure directory exists
    os.makedirs(DATA_PATH, exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8080)
