import os, tempfile, subprocess, time, json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import shutil

app = FastAPI(title="Code Runner (docker-based)")

# Languages configuration: docker image and run command template
LANGS = {
    "python": {"image": "python:3.11-alpine", "cmd": "python /code/source.py"},
    "node": {"image": "node:20-alpine", "cmd": "node /code/source.js"},
    "c": {"image": "gcc:12.2", "cmd": "/bin/sh -c \"gcc /code/source.c -o /code/a.out && /code/a.out\""}
}

@app.post("/run")
async def run(language: str = Form(...), source: UploadFile = File(...), job_id: str = Form(None), timeout: int = Form(5)):
    if language not in LANGS:
        return JSONResponse(status_code=400, content={"ok": False, "error": "unsupported language"})
    contents = await source.read()
    tmp = tempfile.mkdtemp(prefix="run-")
    try:
        # write source to file
        ext = {"python": "py", "node": "js", "c": "c"}[language]
        src_path = os.path.join(tmp, f"source.{ext}")
        with open(src_path, "wb") as f:
            f.write(contents)
        image = LANGS[language]["image"]
        cmd = LANGS[language]["cmd"]
        # run docker container with limits; requires docker daemon on host
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "-v", f"{tmp}:/code:ro",
            image,
            "/bin/sh", "-c", cmd
        ]
        proc = subprocess.Popen(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            return JSONResponse(status_code=504, content={"ok": False, "error": "timeout"})
        return JSONResponse(status_code=200, content={
            "ok": True,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
            "exit_code": exit_code
        })
    finally:
        try:
            shutil.rmtree(tmp)
        except Exception:
            pass
