from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import os
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
        redis_client.lpush("short_term", payload.text)
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
                text("INSERT INTO ltm (id, data) VALUES (:id, :data)"),
                {"id": payload.id, "data": payload.data},
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
    collection.add(documents=[payload.text], ids=[payload.text])
    return {"status": "ok"}


@app.post("/memory/semantic/query")
async def search_memory(payload: QueryPayload):
    results = collection.query(query_texts=[payload.query], n_results=5)
    return results
