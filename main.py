from fastapi.responses import JSONResponse
"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from banner import router as banner_router
from tus import router as tus_router
from db import ensure_banner_table, ensure_tus_table, ensure_database
from facts import router as facts_router
from db import ensure_facts_table
from why import router as why_router
from db import ensure_why_table
from background import router as background_router
from db import ensure_background_table
from core_values import router as core_values_router
from db import ensure_core_values_table
from gallery import router as gallery_router
from db import ensure_gallery_table
from ceo import router as ceo_router
from db import ensure_ceo_table
from members import router as members_router
from db import ensure_members_table
from main_service import router as main_service_router
from db import ensure_main_service_table
from sub_service import router as sub_service_router
from db import ensure_sub_service_table
from service_test import router as service_test_router
from db import ensure_service_test_table

app = FastAPI(title="Glowac API", version="1.0.0")

# Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(banner_router)
app.include_router(tus_router)
app.include_router(facts_router)
app.include_router(why_router)
app.include_router(background_router)
app.include_router(core_values_router)
app.include_router(gallery_router)
app.include_router(ceo_router)
app.include_router(members_router)
app.include_router(main_service_router)
app.include_router(sub_service_router)
app.include_router(service_test_router)


# Utility to test DB connection
def test_db_connection():
    from db import get_database_url
    import psycopg
    try:
        url = get_database_url()
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return True, None
    except Exception as e:
        return False, str(e)

# Add endpoint to test DB connection
@app.get("/db-test", tags=["health"])
def db_test():
    ok, err = test_db_connection()
    if ok:
        return {"db": "ok"}
    return JSONResponse(status_code=500, content={"db": "fail", "error": err})

# @app.on_event("startup")
# def on_startup() -> None:
#     """Initialize database artifacts when the app starts."""
#     ensure_database()
#     ensure_banner_table()
#     ensure_tus_table()
#     ensure_facts_table()
#     ensure_why_table()
#     ensure_background_table()
#     ensure_core_values_table()
#     ensure_gallery_table()
#     ensure_ceo_table()
#     ensure_members_table()
#     ensure_main_service_table()
#     ensure_sub_service_table()
#     ensure_service_test_table()


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    # Test DB connection from CLI
    ok, err = test_db_connection()
    if ok:
        print("Database connection: OK")
    else:
        print(f"Database connection failed: {err}")
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
