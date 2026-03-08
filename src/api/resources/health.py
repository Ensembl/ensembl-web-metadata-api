import os

from fastapi import APIRouter
from sqlalchemy import text
from starlette.responses import JSONResponse

from api.config import DB_URL
from ensembl.utils.database.dbconnection import DBConnection

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def health_live():
    return JSONResponse({"status": "ok"})


@router.get("/health/duckdb")
async def health_duckdb():
    try:
        conn = DBConnection(
            DB_URL, connect_args={"read_only": True, "config": {"memory_limit": "1GB"}}
        )
        with conn.connect() as db_conn:
            db_conn.execute(text("select 1")).scalar()
            genome = db_conn.execute(text("select genome_uuid from genome limit 1")).scalar()
        return JSONResponse(
            {
                "status": "ok",
                "dialect": conn.dialect,
                "db_url": DB_URL,
                "fetched_genome_uuid": genome,
            }
        )
    except Exception as exc:
        return JSONResponse(
            {"status": "error", "db_url": DB_URL, "error": str(exc)}, status_code=500
        )
