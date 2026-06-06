#!/usr/bin/env python3
"""RAG demo: chunk → embed (cached) → upsert into pgvector."""
from dotenv import load_dotenv
load_dotenv()

import argparse
import json
import os
import re
from pathlib import Path

import numpy as np
import psycopg
import voyageai
from pgvector.psycopg import register_vector


# Chunk by section
def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

CACHE_EMB = "embeddings.npy"
CACHE_META = "embeddings_meta.json"


def cache_exists(scratch_dir: Path) -> bool:
    """Return True if both cache files are present."""
    return (scratch_dir / CACHE_EMB).exists() and (scratch_dir / CACHE_META).exists()


def load_cache(scratch_dir: Path) -> tuple[np.ndarray, list[str]]:
    """Load embeddings array and chunk texts from the scratch cache."""
    embeddings = np.load(scratch_dir / CACHE_EMB)
    with open(scratch_dir / CACHE_META, "r") as f:
        chunks = json.load(f)
    return embeddings, chunks


def save_cache(scratch_dir: Path, embeddings: np.ndarray, chunks: list[str]) -> None:
    """Persist embeddings and chunk texts to the scratch cache."""
    scratch_dir.mkdir(parents=True, exist_ok=True)
    np.save(scratch_dir / CACHE_EMB, embeddings)
    with open(scratch_dir / CACHE_META, "w") as f:
        json.dump(chunks, f)
    print(f"Cached {len(chunks)} chunks → {scratch_dir}")


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def generate_embeddings(client: voyageai.Client, chunks: list[str]) -> np.ndarray:
    """Call VoyageAI to embed all chunks; return as float32 numpy array."""
    result = client.embed(chunks, model="voyage-3", input_type="document")
    return np.array(result.embeddings, dtype=np.float32)


# ---------------------------------------------------------------------------
# pgvector
# ---------------------------------------------------------------------------
#  DSN stands for Data Source Name. For PostgreSQL, it is a single string or URL that contains all the required
#  information to locate and connect to your database—including the host, port, database name, username, and password.
# for example
# postgresql://username:password@hostname:port/database_name?sslmode=require
def get_dsn() -> str:
    """Read DATABASE_URL from environment; raise if missing."""
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise EnvironmentError("DATABASE_URL environment variable is not set.")
    return dsn

from psycopg import sql
def ensure_table(cur: psycopg.Cursor, dim: int) -> None:
    """Create the pgvector extension and chunks table if they don't exist."""
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    #cur.execute(f"CREATE TABLE IF NOT EXISTS rag_chunks (id  SERIAL PRIMARY KEY, chunk TEXT NOT NULL,
    # embedding vector({dim}) NOT NULL)")
    # use psycopg.sql
    # sql.SQL(...) creates a safe SQL template.
    #sql.Literal(dim) safely inserts the number (no SQL injection risk, and it satisfies the type checker).
    cur.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS rag_chunks
                (id SERIAL PRIMARY KEY, chunk TEXT NOT NULL, embedding vector({}) NOT NULL )
                """).format(sql.Literal(dim))
    )

def upsert_chunks(cur: psycopg.Cursor, chunks: list[str], embeddings: np.ndarray) -> None:
    """Delete all existing rows and insert fresh chunk+embedding pairs."""
    cur.execute("TRUNCATE TABLE rag_chunks RESTART IDENTITY")
    cur.executemany(
        "INSERT INTO rag_chunks (chunk, embedding) VALUES (%s, %s)",
        [(chunk, emb.tolist()) for chunk, emb in zip(chunks, embeddings)],
    )
    print(f"Upserted {len(chunks)} rows into rag_chunks.")


def ingest_to_pgvector(chunks: list[str], embeddings: np.ndarray) -> None:
    """Open a DB connection and upsert chunks + embeddings into pgvector."""
    dsn = get_dsn()
    dim = embeddings.shape[1]

    with psycopg.connect(dsn) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            ensure_table(cur, dim)
            upsert_chunks(cur, chunks, embeddings)
        conn.commit()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Embed markdown chunks and load into pgvector.")
    parser.add_argument("--input", type=Path, default=Path("./rag_input.md"), help="Markdown input file")
    parser.add_argument("--scratch", type=Path, default=Path("/home/ivana/scratch"), help="Cache directory")
    parser.add_argument("--skip-db", action="store_true", help="Cache embeddings only; skip DB ingestion")
    return parser.parse_args()


def main() -> None:
    """Entry point: embed (or load cache) then upsert into pgvector."""
    args = parse_args()

    # 1. Load or generate embeddings
    if cache_exists(args.scratch):
        print("Cache found — loading embeddings from disk.")
        embeddings, chunks = load_cache(args.scratch)
    else:
        print("No cache found — generating embeddings via VoyageAI.")
        with open(args.input, "r") as f:
            text = f.read()

        chunks = chunk_by_section(text)
        voyage_client = voyageai.Client()
        embeddings = generate_embeddings(voyage_client, chunks)
        save_cache(args.scratch, embeddings, chunks)

    print(f"Loaded {len(chunks)} chunks, embedding dim={embeddings.shape[1]}")

    # 2. Ingest into pgvector
    if not args.skip_db:
        ingest_to_pgvector(chunks, embeddings)


if __name__ == "__main__":
    main()
