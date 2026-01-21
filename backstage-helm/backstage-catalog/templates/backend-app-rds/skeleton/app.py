import os
import logging
import psycopg2
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "local")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS']
        )
        return conn
    except Exception as e:
        logger.error(f"DB Connection failed: {e}")
        return None

@app.get("/")
def read_root():
    conn = get_db_connection()
    if conn:
        status = "Connected to Database!"
        conn.close()
    else:
        status = "Database Connection Failed (Check Secrets)"
        
    return {"message": f"Hello from ${{ values.component_id }}!", "env": APP_ENV, "db_status": status}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ready")
def readiness_check():
    # Only ready if DB connects
    if get_db_connection():
        return {"status": "ready"}
    return {"status": "not_ready"}, 503

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
