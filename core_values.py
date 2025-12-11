"""Routes for managing Core Values (bullet points)."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import CoreValue

router = APIRouter(prefix="/core-values", tags=["core-values"])


@router.get("", response_model=list[CoreValue])
def list_core_values() -> list[CoreValue]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, bullet_text FROM core_values ORDER BY id")
            rows = cur.fetchall()
    return [CoreValue(id=r[0], bullet_text=r[1]) for r in rows]


@router.post("", response_model=CoreValue, status_code=201)
def create_core_value(bullet_text: str = Form(...)) -> CoreValue:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO core_values (bullet_text) VALUES (%s) RETURNING id, bullet_text",
                (bullet_text,),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create core value")
    return CoreValue(id=row[0], bullet_text=row[1])


@router.put("/{cv_id}", response_model=CoreValue)
def update_core_value(cv_id: int, bullet_text: Optional[str] = Form(None)) -> CoreValue:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT bullet_text FROM core_values WHERE id = %s", (cv_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Core value not found")
            cur.execute(
                "UPDATE core_values SET bullet_text = %s WHERE id = %s RETURNING id, bullet_text",
                (bullet_text if bullet_text is not None else current[0], cv_id),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update core value")
    return CoreValue(id=row[0], bullet_text=row[1])


@router.delete("/{cv_id}", status_code=204)
def delete_core_value(cv_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM core_values WHERE id = %s", (cv_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Core value not found")
    return None


__all__ = ["router"]
