"""FastAPI application factory."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from seen.config import BASE_DIR, RESULTS_DIR, setup_logging
from seen.routes import router

load_dotenv()
setup_logging()

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "static" / "images" / "archetypes").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "static" / "images" / "narrators").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SEEN")
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/data", StaticFiles(directory=str(BASE_DIR / "data" / "results")), name="data")
