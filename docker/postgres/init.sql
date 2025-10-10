-- Initialize pgvector and create LTM table
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS ltm (
  id TEXT PRIMARY KEY,
  data JSONB NOT NULL
);
