from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import requests, os, uuid, asyncio, time

# Configuration: set RUNNER_URL to the runner service (http(s)://host:port)
RUNNER_URL = os.getenv("RUNNER_URL", "http://runner:8001")  # in docker-compose or internal network
API_KEY = os.getenv("API_KEY", "change-me")

app = FastAPI(title="CodeAcademy Execution API (proxy to runner)")

def check_api_key(key: str):
    return key == API_KEY

@app.post("/execute")
async def execute(language: str = Form(...), source: UploadFile = File(...), api_key: str = Form(...)):
    if not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="invalid api key")
    src = await source.read()
    job_id = str(uuid.uuid4())
    files = {'source': ('source', src)}
    data = {"language": language, "job_id": job_id, "timeout": "5"}
    # send to runner
    try:
        resp = requests.post(f"{RUNNER_URL}/run", data=data, files=files, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))
    if resp.status_code != 200:
        # pass through runner error
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    return JSONResponse(status_code=200, content=resp.json())

@app.get("/health")
def health():
    return {"ok": True}
