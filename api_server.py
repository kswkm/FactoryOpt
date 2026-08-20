"""
Machine Uptime API Server (FastAPI + PostgreSQL)
DB 자격증명을 보유하는 유일한 컴포넌트.
run.py(Flask 대시보드)는 이 API만 호출한다.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DB_URL")
if not DB_URL:
    raise RuntimeError("DB_URL 환경변수가 설정되지 않았습니다.")

engine = create_engine(DB_URL, pool_pre_ping=True, pool_size=5, max_overflow=5)
TABLE_NAME = "machine_uptime"

app = FastAPI(title="Machine Uptime API", version="1.0.0")


def fetch_all():
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {TABLE_NAME}"))
        return [dict(row._mapping) for row in result]


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB unreachable: {e}")


@app.get("/api/machine-uptime")
def get_machine_uptime(
    machine_id: str | None = Query(default=None, description="특정 machine_id만 필터링"),
):
    try:
        rows = fetch_all()
        if machine_id:
            rows = [r for r in rows if r.get("machine_id") == machine_id]
        return {"success": True, "count": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
def get_summary():
    try:
        rows = fetch_all()
        if not rows:
            return {"success": True, "summary": {}}

        availabilities = [r["availability"] for r in rows if r.get("availability") is not None]
        defect_rates = [r["defect_rate"] for r in rows if r.get("defect_rate") is not None]
        downtimes = [r["downtime_min"] for r in rows if r.get("downtime_min") is not None]
        dates = [r["date_str"] for r in rows if r.get("date_str") is not None]
        machines = {r["machine_id"] for r in rows if r.get("machine_id") is not None}

        summary = {
            "total_records": len(rows),
            "machines": len(machines),
            "avg_availability": sum(availabilities) / len(availabilities) if availabilities else None,
            "avg_defect_rate": sum(defect_rates) / len(defect_rates) if defect_rates else None,
            "total_downtime": sum(downtimes) if downtimes else None,
            "date_range": {
                "start": str(min(dates)) if dates else None,
                "end": str(max(dates)) if dates else None,
            },
        }
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
