"""Routes for managing tus (opening-hours) entries."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import Tus

router = APIRouter(prefix="/tus", tags=["tus"])


@router.get("", response_model=list[Tus])
def list_tus() -> list[Tus]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, day, hours, status FROM tus ORDER BY id")
            rows = cur.fetchall()
    return [Tus(id=r[0], day=r[1], hours=r[2], status=r[3]) for r in rows]


@router.post("", response_model=Tus, status_code=201)
def create_tus(day: str = Form(...), hours: str = Form(...), status: str = Form("Open")) -> Tus:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tus (day, hours, status) VALUES (%s, %s, %s) RETURNING id, day, hours, status",
                (day, hours, status),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create tus entry")
    return Tus(id=row[0], day=row[1], hours=row[2], status=row[3])


@router.put("/{tus_id}", response_model=Tus)
def update_tus(
    tus_id: int,
    day: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
) -> Tus:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT day, hours, status FROM tus WHERE id = %s", (tus_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="tus entry not found")
            cur.execute(
                """
                UPDATE tus
                SET day = %s,
                    hours = %s,
                    status = %s
                WHERE id = %s
                RETURNING id, day, hours, status
                """,
                (
                    day if day is not None else current[0],
                    hours if hours is not None else current[1],
                    status if status is not None else current[2],
                    tus_id,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update tus entry")
    return Tus(id=row[0], day=row[1], hours=row[2], status=row[3])


@router.delete("/{tus_id}", status_code=204)
def delete_tus(tus_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tus WHERE id = %s", (tus_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="tus entry not found")
    return None


__all__ = ["router"]
