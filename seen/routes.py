"""HTTP routes for pages and API endpoints.

Thin handlers only — validation lives in `seen.validation`, gallery loading in
`seen.gallery`, and the reflection pipeline in `seen.logic.reflection`.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from seen.config import QUESTION_LABELS, logger
from seen.gallery import build_archetype_filters, load_gallery_items
from seen.logic import run_reflection
from seen.templates import templates
from seen.utils import (
    all_steps_terminal,
    can_retry,
    normalize_result,
    read_result,
    reload_config,
    text_is_ready,
    write_pending,
)
from seen.validation import ReflectionInputError, validate_reflect_input

router = APIRouter()


def _queue_reflection(
    background_tasks: BackgroundTasks,
    archetype_slug: str,
    question_category: str,
    user_response: str,
    narrator_slug: str,
) -> str:
    uuid_str = str(uuid.uuid4())
    write_pending(
        uuid_str,
        archetype_slug,
        question_category,
        user_response,
        narrator_slug,
    )
    logger.info(
        "Reflection queued uuid=%s archetype=%s narrator=%s question=%s",
        uuid_str,
        archetype_slug,
        narrator_slug,
        question_category,
    )
    background_tasks.add_task(
        run_reflection,
        uuid_str,
        archetype_slug,
        question_category,
        user_response,
        narrator_slug,
    )
    return uuid_str


def _status_payload(data: dict) -> dict:
    data = normalize_result(data)
    steps = data["steps"]
    return {
        "status": data.get("status", "pending"),
        "text_ready": text_is_ready(data),
        "ready": data.get("status") == "ready" or all_steps_terminal(data),
        "steps": {
            step: {
                "status": steps[step]["status"],
                "error": steps[step].get("error"),
            }
            for step in ("text", "image", "voice")
        },
    }


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
    try:
        _, archetypes, narrators = reload_config()
        user_response = validate_reflect_input(
            archetype_slug,
            question_category,
            user_response,
            narrator_slug,
            archetypes=archetypes,
            narrators=narrators,
        )
    except ReflectionInputError as exc:
        raise HTTPException(status_code=400, detail=exc.detail) from exc

    uuid_str = _queue_reflection(
        background_tasks,
        archetype_slug,
        question_category,
        user_response,
        narrator_slug,
    )
    return RedirectResponse(url=f"/processing/{uuid_str}", status_code=303)


@router.post("/reflect/retry/{uuid_str}")
async def retry_reflect(uuid_str: str, background_tasks: BackgroundTasks):
    data = read_result(uuid_str)
    if not data or not can_retry(data):
        raise HTTPException(
            status_code=400,
            detail="Cannot retry — original input was not saved",
        )

    new_uuid = _queue_reflection(
        background_tasks,
        data["archetype_slug"],
        data["question_category"],
        data["user_response"],
        data["narrator_slug"],
    )
    logger.info("Retrying reflection %s as %s", uuid_str, new_uuid)
    return RedirectResponse(url=f"/processing/{new_uuid}", status_code=303)


@router.get("/processing/{uuid_str}")
async def processing_page(request: Request, uuid_str: str):
    return templates.TemplateResponse(
        request, "processing.html", {"uuid": uuid_str}
    )


@router.get("/api/status/{uuid_str}")
async def api_status(uuid_str: str):
    data = read_result(uuid_str)
    if not data:
        return {"status": "pending", "text_ready": False, "ready": False}
    if data.get("status") == "error" and not data.get("reflection"):
        return {
            "status": "error",
            "text_ready": False,
            "ready": False,
            "can_retry": can_retry(data),
            "message": data.get("message", "Unknown error"),
        }
    return _status_payload(data)


@router.get("/api/result/{uuid_str}")
async def api_result(uuid_str: str):
    data = read_result(uuid_str)
    if not data:
        raise HTTPException(status_code=404, detail="Result not found")
    if data.get("status") == "error" and not data.get("reflection"):
        raise HTTPException(status_code=500, detail=data.get("message", "Unknown error"))
    return normalize_result(data)


@router.get("/result/{uuid_str}")
async def result_page(request: Request, uuid_str: str):
    data = read_result(uuid_str)
    if not data:
        raise HTTPException(status_code=404, detail="Result not found")
    if data.get("status") == "error" and not data.get("reflection"):
        raise HTTPException(status_code=500, detail=data.get("message"))
    if not text_is_ready(data):
        return RedirectResponse(url=f"/processing/{uuid_str}", status_code=303)
    return templates.TemplateResponse(
        request,
        "result.html",
        {"result": normalize_result(data)},
    )


@router.get("/gallery")
async def gallery_page(request: Request):
    items = load_gallery_items()
    return templates.TemplateResponse(
        request,
        "gallery.html",
        {
            "items": items,
            "filter_archetypes": build_archetype_filters(items),
        },
    )
