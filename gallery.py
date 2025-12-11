"""Routes for the Environmental Lab Gallery - upload images only."""

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import StreamingResponse

import psycopg

from db import get_dsn
from schemas import Gallery

router = APIRouter(prefix="/gallery", tags=["gallery"])


@router.get("", response_model=list[Gallery])
def list_gallery(request: Request) -> list[Gallery]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, image FROM gallery ORDER BY id")
            rows = cur.fetchall()
    results = []
    for r in rows:
        id_ = r[0]
        preview_url = str(request.url_for("get_gallery_image", gallery_id=id_))
        results.append(Gallery(id=id_, image_preview_url=preview_url))
    return results


@router.post("", response_model=Gallery, status_code=201)
def upload_image(request: Request, image: UploadFile = File(...)) -> Gallery:
    file_contents = image.file.read()
    image.file.close()
    if not file_contents:
        raise HTTPException(status_code=400, detail="Uploaded image file is empty")
    image_mime = image.content_type or "application/octet-stream"

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO gallery (image, image_mime) VALUES (%s, %s) RETURNING id, image, image_mime",
                (psycopg.Binary(file_contents), image_mime),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to store image")
    id_ = row[0]
    preview_url = str(request.url_for("get_gallery_image", gallery_id=id_))
    return Gallery(id=id_, image_preview_url=preview_url)


@router.delete("/{gallery_id}", status_code=204)
def delete_image(gallery_id: int) -> Response:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM gallery WHERE id = %s", (gallery_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Image not found")
    return Response(status_code=204)


@router.get("/{gallery_id}/image", name="get_gallery_image")
def get_gallery_image(gallery_id: int) -> StreamingResponse:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT image, image_mime FROM gallery WHERE id = %s", (gallery_id,))
            row = cur.fetchone()
    if row is None or row[0] is None:
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = row[1] or "application/octet-stream"
    headers = {"Content-Disposition": "inline"}
    return StreamingResponse(iter([bytes(row[0])]), media_type=media_type, headers=headers)


__all__ = ["router"]
