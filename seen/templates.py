"""Jinja2 template engine."""

from fastapi.templating import Jinja2Templates

from seen.config import BASE_DIR

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
