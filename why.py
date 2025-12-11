"""Routes for managing 'Why Choose Us' entries."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import Why

router = APIRouter(prefix="/why", tags=["why"])


@router.get("", response_model=list[Why])
def list_why() -> list[Why]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, label, value, status FROM why_choose_us ORDER BY id")
            rows = cur.fetchall()
    return [Why(id=r[0], label=r[1], value=r[2], status=r[3]) for r in rows]


@router.post("", response_model=Why, status_code=201)
def create_why(label: str = Form(...), value: str = Form(...), status: str = Form("Visible")) -> Why:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO why_choose_us (label, value, status) VALUES (%s, %s, %s) RETURNING id, label, value, status",
                (label, value, status),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create why entry")
    return Why(id=row[0], label=row[1], value=row[2], status=row[3])


@router.put("/{why_id}", response_model=Why)
def update_why(
    why_id: int,
    label: Optional[str] = Form(None),
    value: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
) -> Why:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT label, value, status FROM why_choose_us WHERE id = %s", (why_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Why entry not found")
            cur.execute(
                """
                UPDATE why_choose_us
                SET label = %s,
                    value = %s,
                    status = %s
                WHERE id = %s
                RETURNING id, label, value, status
                """,
                (
                    label if label is not None else current[0],
                    value if value is not None else current[1],
                    status if status is not None else current[2],
                    why_id,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update why entry")
    return Why(id=row[0], label=row[1], value=row[2], status=row[3])


@router.delete("/{why_id}", status_code=204)
def delete_why(why_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM why_choose_us WHERE id = %s", (why_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Why entry not found")
    return None


__all__ = ["router"]
