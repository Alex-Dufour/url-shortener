import hashlib
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, AnyUrl

from .db import get_conn, init_db, insert_or_get, get_by_slug
from .utils import canonicalize, slug_for_canonical

APP_HOST = os.getenv("APP_HOST", "http://localhost:8000")
INITIAL_SLUG_LEN = int(os.getenv("SLUG_LEN", "7"))

app = FastAPI(title="URL Shortener", lifespan=init_db)

class ShortenRequest(BaseModel):
    url: AnyUrl 

class ShortenResponse(BaseModel):
    slug: str
    short_url: str


@app.post("/shorten", response_model=ShortenResponse)
def shorten(body: ShortenRequest, request: Request):
    url_raw = str(body.url)
    try:
        url_canon = canonicalize(url_raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    conn = get_conn()

    for extra in range(0, 6):
        slug_candidate = slug_for_canonical(url_canon, INITIAL_SLUG_LEN + extra) 
        try:
            with conn:
                slug = insert_or_get(conn, url=url_raw, url_canonical=url_canon, slug=slug_candidate)
            return ShortenResponse(slug=slug, short_url=f"{APP_HOST}/{slug}")
        except Exception as ex:
            msg = str(ex).lower()
            if "unique" in msg and "slug" in msg:
                continue
            raise

    raise HTTPException(status_code=500, detail="Could not allocate slug")

@app.get("/{slug}")
def redirect(slug: str):
    conn = get_conn()
    row = get_by_slug(conn, slug)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    return RedirectResponse(url=row["url"], status_code=307)
