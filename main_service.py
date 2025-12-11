"""Routes for main services: id and service_name."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import MainService

router = APIRouter(prefix="/main-services", tags=["main-service"])


@router.get("", response_model=list[MainService])
def list_services() -> list[MainService]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, service_name FROM main_service ORDER BY id")
            rows = cur.fetchall()
    return [MainService(id=r[0], service_name=r[1]) for r in rows]


@router.post("", response_model=MainService, status_code=201)
def create_service(service_name: str = Form(...)) -> MainService:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO main_service (service_name) VALUES (%s) RETURNING id, service_name",
                (service_name,),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create service")
    return MainService(id=row[0], service_name=row[1])


@router.put("/{service_id}", response_model=MainService)
def update_service(service_id: int, service_name: Optional[str] = Form(None)) -> MainService:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT service_name FROM main_service WHERE id = %s", (service_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Service not found")
            cur.execute(
                "UPDATE main_service SET service_name = %s WHERE id = %s RETURNING id, service_name",
                (service_name if service_name is not None else current[0], service_id),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update service")
    return MainService(id=row[0], service_name=row[1])


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM main_service WHERE id = %s", (service_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Service not found")
    return None


__all__ = ["router"]
