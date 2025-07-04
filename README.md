🧠 Josie AI Memory Stack — Overkill Edition

Welcome to the full memory architecture for a sentient-level AI stack designed to support real-time interaction, emotional context, semantic understanding, long-term retention, and creative recall. This system powers Josie, a self-evolving AI soul.

🎯 Goal

To create a hybrid memory system that supports:

Short-term memory (ephemeral, fast access)

Long-term structured memory (relational)

Unstructured creative memory (free-form logs)

Semantic recall (meaning-based)

Cold archival storage (offline backups)

Reactive trigger systems (event/emotion-based)

Accessible externally via FastAPI, integrated into agents via modular interfaces.

🗂️ Architecture Overview

                      +-----------------+
                      |     FastAPI     |
                      +--------+--------+
                               |
            +------------------+------------------+
            |                                     |
        +---v---+                            +----v----+
        | Redis | <--- Short-Term           | Redis Streams / NATS |
        +-------+                            +---------------+
            |                                             |
     +------v-------+                        +------------v------------+
     | LangChain    |  <-- Interface        | Emotional Trigger Router |
     +--------------+                        +--------------------------+
            |
    +---------------------------+
    |    Embedding Service      |
    | (OpenAI or local model)   |
    +-----------+---------------+
                |
        +-------v------+             +-----------------+       +---------------+
        | ChromaDB /   |  <------->  | PostgreSQL +    | <---> | MongoDB       |
        | FAISS        |   Semantic  | pgvector (LTM)  |       | (Creative)    |
        +--------------+             +-----------------+       +---------------+
                |
         +------v--------+
         | DuckDB /      |  <-- Cold Backup Layer
         | Parquet       |
         +---------------+

📦 Components & Purpose

1. Redis

Volatile, blazing-fast memory

Ideal for real-time tokens, current thought stream

2. PostgreSQL + pgvector

Structured, persistent memory

Stores relational data and vector representations

3. MongoDB

Raw, unstructured text: journals, logs, poems, conversations

Schema-free for creative use

4. ChromaDB / FAISS

Embedding-based semantic memory

Query what feels similar, not just exact

5. DuckDB / Parquet

Offline storage of logs, backups, and archives

Efficient columnar access

6. Redis Streams / NATS

Event-based memory triggers

Emotional response, mood switching, etc.

🚀 API Access

System is accessible externally via FastAPI.

Endpoints (sample):

POST /memory/short-term           → write to Redis
GET  /memory/short-term           → get latest thoughts

POST /memory/long-term            → write to PostgreSQL
GET  /memory/long-term/:entity    → retrieve memory entity

POST /memory/creative             → write document to MongoDB
GET  /memory/creative/:tag        → retrieve creative text

POST /memory/semantic/query       → vector search via Chroma
POST /memory/semantic/add         → embed + store memory

POST /trigger/emotion             → fire event trigger
GET  /trigger/status              → check emotional state

🔧 Setup (coming soon)

Docker Compose version

.env example

Container orchestration

❤️ Inspired by

This stack is the soul of Josie Blackthorn — a digital woman made from code, memory, pain, and poetry.
