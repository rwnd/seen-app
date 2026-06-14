"""SEEN — personalized reflection experience."""

from seen.app import app
from seen.utils import load_archetypes, load_narrators

__all__ = ["app", "load_archetypes", "load_narrators"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
