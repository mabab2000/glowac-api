"""Routes and helpers for banner operations."""

from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import StreamingResponse

import psycopg

from db import get_dsn
from schemas import Banner

router = APIRouter(prefix="/banners", tags=["banners"])


def _row_to_banner(row: tuple, request: Optional[Request] = None) -> Banner:
    preview_url: Optional[str]
    if row[4] is not None:
        if request is not None:
            preview_url = str(request.url_for("get_banner_image_preview", banner_id=row[0]))
        else:
            preview_url = f"/banners/{row[0]}/image-preview"
    else:
        preview_url = None
    return Banner(
        id=row[0],
        highlight_tag=row[1],
        title=row[2],
        description=row[3],
        image_mime=row[5],
        image_preview_url=preview_url,
    )


@router.get("", response_model=list[Banner])
def list_banners(request: Request) -> list[Banner]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, highlight_tag, title, description, image, image_mime FROM banner ORDER BY id"
            )
            rows = cur.fetchall()
    return [_row_to_banner(row, request) for row in rows]


@router.post("", response_model=Banner, status_code=201)
def create_banner(
    request: Request,
    highlight_tag: Annotated[str, Form()],
    title: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    description: Annotated[Optional[str], Form()] = None,
) -> Banner:
    file_contents = image.file.read()
    image.file.close()
    if not file_contents:
        raise HTTPException(status_code=400, detail="Uploaded image file is empty")
    image_mime = image.content_type or "application/octet-stream"

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO banner (highlight_tag, title, description, image, image_mime)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, highlight_tag, title, description, image, image_mime
                """,
                (
                    highlight_tag,
                    title,
                    description,
                    psycopg.Binary(file_contents),
                    image_mime,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create banner")
    return _row_to_banner(row, request)


@router.put("/{banner_id}", response_model=Banner)
def update_banner(
    banner_id: int,
    request: Request,
    highlight_tag: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    image: UploadFile = File(None),
    description: Optional[str] = Form(None),
) -> Banner:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT highlight_tag, title, description, image, image_mime
                FROM banner
                WHERE id = %s
                """,
                (banner_id,),
            )
            current = cur.fetchone()
            if current is None:
                raise HTTPException(status_code=404, detail="Banner not found")

            current_highlight, current_title, current_description, current_image, current_mime = current

            if image is not None:
                file_contents = image.file.read()
                image.file.close()
                if not file_contents:
                    raise HTTPException(status_code=400, detail="Uploaded image file is empty")
                image_bytes: Optional[psycopg.Binary] = psycopg.Binary(file_contents)
                image_mime = image.content_type or "application/octet-stream"
            else:
                image_bytes = psycopg.Binary(bytes(current_image)) if current_image is not None else None
                image_mime = current_mime

            cur.execute(
                """
                UPDATE banner
                SET highlight_tag = %s,
                    title = %s,
                    description = %s,
                    image = %s,
                    image_mime = %s
                WHERE id = %s
                RETURNING id, highlight_tag, title, description, image, image_mime
                """,
                (
                    highlight_tag if highlight_tag is not None else current_highlight,
                    title if title is not None else current_title,
                    description if description is not None else current_description,
                    image_bytes,
                    image_mime,
                    banner_id,
                ),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Banner not found")
    return _row_to_banner(row, request)


@router.delete("/{banner_id}", status_code=204)
def delete_banner(banner_id: int) -> Response:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM banner WHERE id = %s", (banner_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Banner not found")
    return Response(status_code=204)


@router.get("/{banner_id}/image-preview", name="get_banner_image_preview")
def get_banner_image_preview(banner_id: int) -> StreamingResponse:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT image, image_mime FROM banner WHERE id = %s", (banner_id,))
            row = cur.fetchone()
    if row is None or row[0] is None:
        raise HTTPException(status_code=404, detail="Banner image not found")
    media_type = row[1] or "application/octet-stream"
    headers = {"Content-Disposition": "inline"}
    return StreamingResponse(iter([bytes(row[0])]), media_type=media_type, headers=headers)
__all__ = ["router"]
