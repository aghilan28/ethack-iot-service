from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI(title="Member 1 - IoT Core API Backend")

# Enable CORS so Member 4's frontend dashboard can read your data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "service": "iot-core-backend"}

@app.get("/api/telemetry/latest")
def get_latest_telemetry(limit: int = 10):
    """Fetches the live database rows directly from the docker container"""
    sql = f"SELECT json_build_object('id', id, 'timestamp', timestamp, 'machine_id', machine_id, 'measured_value', measured_value) FROM industrial.telemetry ORDER BY timestamp DESC LIMIT {limit};"
    
    cmd = ["docker", "exec", "-i", "iob_postgres_db", "psql", "-U", "postgres", "-d", "iob", "-t", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        rows = [json.loads(line.strip()) for line in result.stdout.splitlines() if line.strip()]
        return {"success": True, "data": rows}
    else:
        return {"success": False, "error": result.stderr.strip()}
