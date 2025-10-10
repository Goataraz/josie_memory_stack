from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os
import json
import hashlib
import redis
from redis.exceptions import RedisError
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import chromadb


app = FastAPI(title="Josie AI Memory Stack")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
POSTGRES_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost/postgres")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
SHORT_TERM_MAX_LEN = int(os.environ.get("SHORT_TERM_MAX_LEN", "1000"))
SHORT_TERM_TTL_SECONDS: Optional[int] = (
    int(os.environ["SHORT_TERM_TTL_SECONDS"]) if os.environ.get("SHORT_TERM_TTL_SECONDS") else None
)

redis_client = redis.Redis.from_url(REDIS_URL)

mongo_client = AsyncIOMotorClient(MONGO_URL)
creative_db = mongo_client["creative"]

engine = create_engine(POSTGRES_URL, future=True)

# Attempt to connect to a Chroma server. Fallback to in-memory client during
# tests or if the server is unavailable.
try:
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
except Exception:
    chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("memory")

@app.get("/", tags=["health"])
async def read_root():
    return {"status": "ok"}


@app.get("/health/live", tags=["health"])
async def live():
    return {"status": "live"}


@app.get("/health/ready", tags=["health"])
async def ready():
    checks: Dict[str, Any] = {}
    # Redis
    try:
        checks["redis"] = bool(redis_client.ping())
    except Exception as e:
        checks["redis"] = {"ok": False, "error": str(e)}
    # Postgres
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception as e:
        checks["postgres"] = {"ok": False, "error": str(e)}
    # Mongo
    try:
        await mongo_client.admin.command("ping")
        checks["mongo"] = True
    except Exception as e:
        checks["mongo"] = {"ok": False, "error": str(e)}
    # Chroma (best-effort)
    try:
        # Query small count to verify collection is responsive
        _ = collection.count()  # type: ignore[attr-defined]
        checks["chroma"] = True
    except Exception as e:
        checks["chroma"] = {"ok": False, "error": str(e)}
    overall_ok = all(v is True for v in checks.values())
    if not overall_ok:
        raise HTTPException(status_code=503, detail=checks)
    return {"status": "ready", **checks}


@app.on_event("startup")
async def on_startup():
    # Ensure Postgres schema exists
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "CREATE TABLE IF NOT EXISTS ltm (id TEXT PRIMARY KEY, data JSONB NOT NULL)"
            ))
    except Exception:
        # Defer to runtime errors on first use; readiness will surface issues
        pass


@app.on_event("shutdown")
async def on_shutdown():
    try:
        mongo_client.close()
    except Exception:
        pass
    try:
        engine.dispose()
    except Exception:
        pass
    try:
        redis_client.close()
    except Exception:
        pass



class TextPayload(BaseModel):
    text: str

class LongTermPayload(BaseModel):
    id: str
    data: Dict[str, Any]

class CreativePayload(BaseModel):
    tag: str
    body: str

class QueryPayload(BaseModel):
    query: str


@app.post("/memory/short-term")
async def store_short_term(payload: TextPayload):
    try:
        key = "short_term"
        redis_client.lpush(key, payload.text)
        # Trim to bounded length to prevent unbounded growth
        if SHORT_TERM_MAX_LEN > 0:
            redis_client.ltrim(key, 0, SHORT_TERM_MAX_LEN - 1)
        # Optional TTL for the list key
        if SHORT_TERM_TTL_SECONDS and SHORT_TERM_TTL_SECONDS > 0:
            redis_client.expire(key, SHORT_TERM_TTL_SECONDS)
        return {"status": "ok"}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/short-term")
async def get_short_term():
    try:
        messages = redis_client.lrange("short_term", 0, -1)
        return {"memory": [m.decode("utf-8") for m in messages]}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/long-term")
async def add_long_term(payload: LongTermPayload):
    try:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO ltm (id, data) VALUES (:id, :data::jsonb)"),
                {"id": payload.id, "data": json.dumps(payload.data)},
            )
        return {"status": "ok"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/creative")
async def save_creative(payload: CreativePayload):
    await creative_db.logs.insert_one(payload.dict())
    return {"status": "ok"}


@app.post("/memory/semantic/add")
async def embed_memory(payload: TextPayload):
    # Deterministic ID based on content hash to deduplicate
    memory_id = hashlib.sha256(payload.text.encode("utf-8")).hexdigest()
    collection.add(documents=[payload.text], ids=[memory_id])
    return {"status": "ok", "id": memory_id}


@app.post("/memory/semantic/query")
async def search_memory(payload: QueryPayload):
    results = collection.query(query_texts=[payload.query], n_results=5)
    return results
