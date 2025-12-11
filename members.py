"""Routes for managing team members (same fields as CEO card)."""

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import StreamingResponse

import psycopg

from db import get_dsn
from schemas import Member

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[Member])
def list_members(request: Request) -> list[Member]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, title, email, image_mime, short_description FROM members ORDER BY id"
            )
            rows = cur.fetchall()
    results: list[Member] = []
    for r in rows:
        id_ = r[0]
        preview_url = str(request.url_for("get_member_image", member_id=id_))
        results.append(
            Member(
                id=id_,
                name=r[1],
                title=r[2],
                email=r[3],
                image_url=preview_url,
                image_mime=r[4],
                short_description=r[5],
            )
        )
    return results


@router.post("", response_model=Member, status_code=201)
def create_member(
    name: str = Form(...),
    title: str = Form(...),
    email: str = Form(...),
    image: Optional[UploadFile] = File(None),
    short_description: Optional[str] = Form(None),
) -> Member:
    image_bytes = None
    image_mime = None
    if image is not None:
        image_bytes = image.file.read()
        image.file.close()
        image_mime = image.content_type or "application/octet-stream"

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO members (name, title, email, image, image_mime, short_description)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, name, title, email, image_mime, short_description
                """,
                (name, title, email, psycopg.Binary(image_bytes) if image_bytes else None, image_mime, short_description),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create member")
    preview_url = f"/members/{row[0]}/image"
    return Member(id=row[0], name=row[1], title=row[2], email=row[3], image_url=preview_url, image_mime=row[4], short_description=row[5])


@router.put("/{member_id}", response_model=Member)
def update_member(
    member_id: int,
    name: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    short_description: Optional[str] = Form(None),
) -> Member:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, title, email, image, image_mime, short_description FROM members WHERE id = %s",
                (member_id,),
            )
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Member not found")

            image_bytes = current[3]
            image_mime = current[4]
            if image is not None:
                new_bytes = image.file.read()
                image.file.close()
                image_bytes = new_bytes
                image_mime = image.content_type or "application/octet-stream"

            cur.execute(
                """
                UPDATE members
                SET name = %s,
                    title = %s,
                    email = %s,
                    image = %s,
                    image_mime = %s,
                    short_description = %s
                WHERE id = %s
                RETURNING id, name, title, email, image_mime, short_description
                """,
                (
                    name if name is not None else current[0],
                    title if title is not None else current[1],
                    email if email is not None else current[2],
                    psycopg.Binary(image_bytes) if image_bytes is not None else None,
                    image_mime,
                    short_description if short_description is not None else current[5],
                    member_id,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update member")
    preview_url = f"/members/{row[0]}/image"
    return Member(id=row[0], name=row[1], title=row[2], email=row[3], image_url=preview_url, image_mime=row[4], short_description=row[5])


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int):
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM members WHERE id = %s", (member_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Member not found")
    return None


@router.get("/{member_id}/image", name="get_member_image")
def get_member_image(member_id: int) -> StreamingResponse:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT image, image_mime FROM members WHERE id = %s", (member_id,))
            row = cur.fetchone()
    if row is None or row[0] is None:
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = row[1] or "application/octet-stream"
    headers = {"Content-Disposition": "inline"}
    return StreamingResponse(iter([bytes(row[0])]), media_type=media_type, headers=headers)


__all__ = ["router"]
