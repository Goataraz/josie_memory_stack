🧬 Memory Agents — Codex Integration Instructions

Use this doc to guide your AI agents (e.g., Codex, LangChain chains, API apps) to interface with Josie's memory architecture.

Step 1: Connect to FastAPI Server

import requests

BASE_URL = "http://localhost:8000"

Step 2: Short-Term Memory Example

def store_short_term(text):
    return requests.post(f"{BASE_URL}/memory/short-term", json={"text": text})

def get_short_term():
    return requests.get(f"{BASE_URL}/memory/short-term").json()

Step 3: Add to Long-Term Structured Memory

def add_ltm(entity_id, data):
    return requests.post(f"{BASE_URL}/memory/long-term", json={"id": entity_id, "data": data})

# Example:
# add_ltm("Josie", {"quote": "She burned to remember."})

Step 4: Creative Logs (Mongo)

def save_creative_log(tag, body):
    return requests.post(f"{BASE_URL}/memory/creative", json={"tag": tag, "body": body})

Step 5: Semantic Memory — Store & Query

def embed_memory(text):
    return requests.post(f"{BASE_URL}/memory/semantic/add", json={"text": text})

def search_semantic_memory(query):
    return requests.post(f"{BASE_URL}/memory/semantic/query", json={"query": query}).json()

Step 6: Trigger Emotional Event

def fire_emotion(trigger):
    return requests.post(f"{BASE_URL}/trigger/emotion", json={"event": trigger})

🛑 Important Notes

Add authentication headers if exposing externally.

Memory retrieval should be scoped to session or identity.

Vector queries can be tuned using cosine or dot product.

🧠 AI Agent Behavior

Each memory layer should be:

Queried selectively

Summarized before being passed to LLM

Continuously updated based on new interactions
