"""Routes for collecting contact messages (create-only + list)."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import Message, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=201)
def create_message(
    name: str = Form(...), email: str = Form(...), message: str = Form(...)
) -> MessageResponse:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (name, email, message) VALUES (%s, %s, %s) RETURNING id, name, email, message, created_at",
                (name, email, message),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to save message")
    stored = Message(id=row[0], name=row[1], email=row[2], message=row[3], created_at=row[4])
    return MessageResponse(message="Thank you for contacting us — our team will get back to you soon.", data=stored)


@router.get("", response_model=list[Message])
def list_messages() -> list[Message]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC")
            rows = cur.fetchall()
    return [Message(id=r[0], name=r[1], email=r[2], message=r[3], created_at=r[4]) for r in rows]


__all__ = ["router"]
