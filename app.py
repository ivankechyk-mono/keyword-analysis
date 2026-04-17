import json
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

DATA_FILE = Path(__file__).parent / "data" / "dashboard_data.json"
TEMPLATES_DIR = Path(__file__).parent / "templates"

app = FastAPI(title="Monobank Keyword Dashboard")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

_refresh_status = {"running": False, "last_error": None}


def _run_pipeline():
    _refresh_status["running"] = True
    _refresh_status["last_error"] = None
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            _refresh_status["last_error"] = result.stderr[-2000:] if result.stderr else "Unknown error"
    except Exception as e:
        _refresh_status["last_error"] = str(e)
    finally:
        _refresh_status["running"] = False


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/api/data")
async def get_data():
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="No data yet. Click 'Refresh' to collect data.")
    with open(DATA_FILE, encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


@app.post("/api/refresh")
async def refresh(background_tasks: BackgroundTasks):
    if _refresh_status["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(_run_pipeline)
    return {"status": "started"}


@app.get("/api/refresh/status")
async def refresh_status():
    return _refresh_status
