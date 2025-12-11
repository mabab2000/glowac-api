"""Routes for SubService entities linked to MainService."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import SubService

router = APIRouter(prefix="/sub-services", tags=["sub-service"])


@router.get("/by-main/{main_service_id}", response_model=list[SubService])
def list_sub_services_by_main(main_service_id: int) -> list[SubService]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, main_service_id, service_name, description FROM sub_service WHERE main_service_id = %s ORDER BY id",
                (main_service_id,),
            )
            rows = cur.fetchall()
    return [SubService(id=r[0], main_service_id=r[1], service_name=r[2], description=r[3]) for r in rows]


@router.post("/by-main/{main_service_id}", response_model=SubService, status_code=201)
def create_sub_service_for_main(
    main_service_id: int, service_name: str = Form(...), description: Optional[str] = Form(None)
) -> SubService:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            # ensure main service exists
            cur.execute("SELECT id FROM main_service WHERE id = %s", (main_service_id,))
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Main service not found")
            cur.execute(
                "INSERT INTO sub_service (main_service_id, service_name, description) VALUES (%s, %s, %s) RETURNING id, main_service_id, service_name, description",
                (main_service_id, service_name, description),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create sub-service")
    return SubService(id=row[0], main_service_id=row[1], service_name=row[2], description=row[3])


@router.get("/{sub_id}", response_model=SubService)
def get_sub_service(sub_id: int) -> SubService:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, main_service_id, service_name, description FROM sub_service WHERE id = %s", (sub_id,))
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Sub-service not found")
    return SubService(id=row[0], main_service_id=row[1], service_name=row[2], description=row[3])


@router.put("/{sub_id}", response_model=SubService)
def update_sub_service(
    sub_id: int,
    main_service_id: Optional[int] = Form(None),
    service_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
) -> SubService:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT main_service_id, service_name, description FROM sub_service WHERE id = %s", (sub_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Sub-service not found")

            new_main = main_service_id if main_service_id is not None else current[0]
            # if main_service_id changed, ensure target main exists
            if main_service_id is not None:
                cur.execute("SELECT id FROM main_service WHERE id = %s", (main_service_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Target main service not found")

            cur.execute(
                "UPDATE sub_service SET main_service_id = %s, service_name = %s, description = %s WHERE id = %s RETURNING id, main_service_id, service_name, description",
                (
                    new_main,
                    service_name if service_name is not None else current[1],
                    description if description is not None else current[2],
                    sub_id,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update sub-service")
    return SubService(id=row[0], main_service_id=row[1], service_name=row[2], description=row[3])


@router.delete("/{sub_id}", status_code=204)
def delete_sub_service(sub_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sub_service WHERE id = %s", (sub_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Sub-service not found")
    return None


__all__ = ["router"]
