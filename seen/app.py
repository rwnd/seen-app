"""FastAPI application factory."""

import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from seen.config import BASE_DIR, RESULTS_DIR, logger, setup_logging
from seen.routes import router
from seen.samples import seed_sample_results_if_empty

load_dotenv()
setup_logging()

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
seed_sample_results_if_empty()
(BASE_DIR / "static" / "images" / "archetypes").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "static" / "images" / "narrators").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SEEN")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    if not request.url.path.startswith("/static"):
        logger.info(
            "%s %s -> %s (%.0fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
    return response


app.include_router(router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/data", StaticFiles(directory=str(BASE_DIR / "data" / "results")), name="data")
docs_assets = BASE_DIR / "docs" / "assets"
if docs_assets.is_dir():
    app.mount("/docs-assets", StaticFiles(directory=str(docs_assets)), name="docs_assets")
