"""Routes for managing Background Section paragraphs."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import Background

router = APIRouter(prefix="/background", tags=["background"])


@router.get("", response_model=list[Background])
def list_background() -> list[Background]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, paragraph FROM background ORDER BY id")
            rows = cur.fetchall()
    return [Background(id=r[0], paragraph=r[1]) for r in rows]


@router.post("", response_model=Background, status_code=201)
def create_background(paragraph: str = Form(...)) -> Background:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO background (paragraph) VALUES (%s) RETURNING id, paragraph",
                (paragraph,),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create background paragraph")
    return Background(id=row[0], paragraph=row[1])


@router.put("/{bg_id}", response_model=Background)
def update_background(bg_id: int, paragraph: Optional[str] = Form(None)) -> Background:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT paragraph FROM background WHERE id = %s", (bg_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Background paragraph not found")
            cur.execute(
                "UPDATE background SET paragraph = %s WHERE id = %s RETURNING id, paragraph",
                (paragraph if paragraph is not None else current[0], bg_id),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update background paragraph")
    return Background(id=row[0], paragraph=row[1])


@router.delete("/{bg_id}", status_code=204)
def delete_background(bg_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM background WHERE id = %s", (bg_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Background paragraph not found")
    return None


__all__ = ["router"]
