"""Routes for managing Facts & Figures (homepage stats)."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import Fact

router = APIRouter(prefix="/facts", tags=["facts"])


@router.get("", response_model=list[Fact])
def list_facts() -> list[Fact]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, label, number, status FROM facts ORDER BY id")
            rows = cur.fetchall()
    return [Fact(id=r[0], label=r[1], number=int(r[2]), status=r[3]) for r in rows]


@router.post("", response_model=Fact, status_code=201)
def create_fact(label: str = Form(...), number: int = Form(...), status: str = Form("Visible")) -> Fact:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO facts (label, number, status) VALUES (%s, %s, %s) RETURNING id, label, number, status",
                (label, number, status),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create fact")
    return Fact(id=row[0], label=row[1], number=int(row[2]), status=row[3])


@router.put("/{fact_id}", response_model=Fact)
def update_fact(
    fact_id: int,
    label: Optional[str] = Form(None),
    number: Optional[int] = Form(None),
    status: Optional[str] = Form(None),
) -> Fact:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT label, number, status FROM facts WHERE id = %s", (fact_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Fact not found")
            cur.execute(
                """
                UPDATE facts
                SET label = %s,
                    number = %s,
                    status = %s
                WHERE id = %s
                RETURNING id, label, number, status
                """,
                (
                    label if label is not None else current[0],
                    number if number is not None else current[1],
                    status if status is not None else current[2],
                    fact_id,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update fact")
    return Fact(id=row[0], label=row[1], number=int(row[2]), status=row[3])


@router.delete("/{fact_id}", status_code=204)
def delete_fact(fact_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM facts WHERE id = %s", (fact_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Fact not found")
    return None


__all__ = ["router"]
