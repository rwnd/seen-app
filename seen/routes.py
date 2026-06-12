"""HTTP routes for pages and API endpoints."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from seen.config import QUESTION_LABELS, RESULTS_DIR
from seen.logic import run_reflection
from seen.templates import templates
from seen.utils import reload_config, result_path

router = APIRouter()


@router.get("/")
async def input_page(request: Request):
    categories, archetypes, narrators = reload_config()
    return templates.TemplateResponse(
        request,
        "input.html",
        {
            "categories": categories,
            "archetypes": archetypes,
            "narrators": narrators,
            "question_labels": QUESTION_LABELS,
        },
    )


@router.post("/reflect")
async def reflect(
    background_tasks: BackgroundTasks,
    archetype_slug: str = Form(...),
    question_category: str = Form(...),
    user_response: str = Form(...),
    narrator_slug: str = Form(...),
):
    user_response = user_response.strip()
    if len(user_response) < 20:
        raise HTTPException(status_code=400, detail="Response must be at least 20 characters")

    _, archetypes, narrators = reload_config()
    if archetype_slug not in archetypes:
        raise HTTPException(status_code=400, detail="Unknown archetype")
    if narrator_slug not in narrators:
        raise HTTPException(status_code=400, detail="Unknown narrator")
    if question_category not in QUESTION_LABELS:
        raise HTTPException(status_code=400, detail="Unknown question category")

    uuid_str = str(uuid.uuid4())
    background_tasks.add_task(
        run_reflection,
        uuid_str,
        archetype_slug,
        question_category,
        user_response,
        narrator_slug,
    )
    return RedirectResponse(url=f"/processing/{uuid_str}", status_code=303)


@router.get("/processing/{uuid_str}")
async def processing_page(request: Request, uuid_str: str):
    return templates.TemplateResponse(
        request, "processing.html", {"uuid": uuid_str}
    )


@router.get("/api/status/{uuid_str}")
async def api_status(uuid_str: str):
    path = result_path(uuid_str)
    if not path.exists():
        return {"status": "pending"}
    data = json.loads(path.read_text())
    if data.get("status") == "error":
        return {"status": "error", "message": data.get("message", "Unknown error")}
    return {"status": "ready"}


@router.get("/result/{uuid_str}")
async def result_page(request: Request, uuid_str: str):
    path = result_path(uuid_str)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    data = json.loads(path.read_text())
    if data.get("status") == "error":
        raise HTTPException(status_code=500, detail=data.get("message"))
    return templates.TemplateResponse(request, "result.html", {"result": data})


@router.get("/gallery")
async def gallery_page(request: Request):
    items = []
    for path in RESULTS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if data.get("status") == "error" or "the_line" not in data:
            continue
        items.append(data)
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return templates.TemplateResponse(request, "gallery.html", {"items": items})
