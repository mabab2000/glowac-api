"""Routes for Requesting Geotechnical Services (create + list)."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import GeotechRequest

router = APIRouter(prefix="/geotech-requests", tags=["geotech"])


@router.post("", response_model=GeotechRequest, status_code=201)
def create_geotech_request(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    project_details: str = Form(...),
) -> GeotechRequest:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO geotech_requests (name, email, phone, project_details) VALUES (%s, %s, %s, %s) RETURNING id, name, email, phone, project_details, created_at",
                (name, email, phone, project_details),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to save request")
    return GeotechRequest(id=row[0], name=row[1], email=row[2], phone=row[3], project_details=row[4], created_at=row[5])


@router.get("", response_model=list[GeotechRequest])
def list_geotech_requests() -> list[GeotechRequest]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, phone, project_details, created_at FROM geotech_requests ORDER BY created_at DESC")
            rows = cur.fetchall()
    return [GeotechRequest(id=r[0], name=r[1], email=r[2], phone=r[3], project_details=r[4], created_at=r[5]) for r in rows]


__all__ = ["router"]
