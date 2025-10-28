from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os, uuid
import httpx

# Configuration
RUNNER_URL = os.getenv("RUNNER_URL", "http://runner:8001")
API_KEY = os.getenv("API_KEY", "letmeinboss")

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

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{RUNNER_URL}/run", data=data, files=files)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Runner request failed: {str(e)}")

    try:
        resp_json = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Invalid JSON response from runner")

    return JSONResponse(status_code=resp.status_code, content=resp_json)

@app.get("/health")
def health():
    return {"ok": True}

# If running directly with Python (optional for Fly.io)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
