"""Routes for ServiceTest entities (linked to main_service and sub_service)."""

from typing import Optional

from fastapi import APIRouter, Form, HTTPException

import psycopg

from db import get_dsn
from schemas import ServiceTest

router = APIRouter(prefix="/service-tests", tags=["service-test"])


@router.get("/by-sub/{sub_service_id}", response_model=list[ServiceTest])
def list_tests_by_sub(sub_service_id: int) -> list[ServiceTest]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, main_service_id, sub_service_id, test_name, description FROM service_test WHERE sub_service_id = %s ORDER BY id",
                (sub_service_id,),
            )
            rows = cur.fetchall()
    return [ServiceTest(id=r[0], main_service_id=r[1], sub_service_id=r[2], test_name=r[3], description=r[4]) for r in rows]

@router.post("", response_model=ServiceTest, status_code=201)
def create_service_test(
    sub_service_id: int = Form(...),
    test_name: str = Form(...),
    description: Optional[str] = Form(None),
) -> ServiceTest:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            # validate sub_service exists and fetch its main_service_id
            cur.execute("SELECT main_service_id FROM sub_service WHERE id = %s", (sub_service_id,))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Sub-service not found")
            main_service_id = row[0]

            cur.execute(
                "INSERT INTO service_test (main_service_id, sub_service_id, test_name, description) VALUES (%s, %s, %s, %s) RETURNING id, main_service_id, sub_service_id, test_name, description",
                (main_service_id, sub_service_id, test_name, description),
            )
            created = cur.fetchone()
    if created is None:
        raise HTTPException(status_code=500, detail="Failed to create service test")
    return ServiceTest(id=created[0], main_service_id=created[1], sub_service_id=created[2], test_name=created[3], description=created[4])


@router.get("/{test_id}", response_model=ServiceTest)
def get_service_test(test_id: int) -> ServiceTest:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, main_service_id, sub_service_id, test_name, description FROM service_test WHERE id = %s", (test_id,))
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Service test not found")
    return ServiceTest(id=row[0], main_service_id=row[1], sub_service_id=row[2], test_name=row[3], description=row[4])


@router.put("/{test_id}", response_model=ServiceTest)
def update_service_test(
    test_id: int,
    sub_service_id: Optional[int] = Form(None),
    test_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
) -> ServiceTest:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT main_service_id, sub_service_id, test_name, description FROM service_test WHERE id = %s", (test_id,))
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Service test not found")
            # determine new sub and main; if sub_service_id provided, validate and derive main
            new_sub = sub_service_id if sub_service_id is not None else current[1]
            if sub_service_id is not None:
                cur.execute("SELECT main_service_id FROM sub_service WHERE id = %s", (new_sub,))
                sub_row = cur.fetchone()
                if sub_row is None:
                    raise HTTPException(status_code=404, detail="Sub-service not found")
                new_main = sub_row[0]
            else:
                new_main = current[0]

            cur.execute(
                "UPDATE service_test SET main_service_id = %s, sub_service_id = %s, test_name = %s, description = %s WHERE id = %s RETURNING id, main_service_id, sub_service_id, test_name, description",
                (
                    new_main,
                    new_sub,
                    test_name if test_name is not None else current[2],
                    description if description is not None else current[3],
                    test_id,
                ),
            )
            updated = cur.fetchone()
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update service test")
    return ServiceTest(id=updated[0], main_service_id=updated[1], sub_service_id=updated[2], test_name=updated[3], description=updated[4])


@router.delete("/{test_id}", status_code=204)
def delete_service_test(test_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM service_test WHERE id = %s", (test_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Service test not found")
    return None


__all__ = ["router"]
