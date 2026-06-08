#!/usr/bin/env python3
"""RAG demo: search vector database using the query embedding"""
from dotenv import load_dotenv
load_dotenv()

import psycopg
import voyageai

from pg_utils import get_dsn



def main() -> None:

    query = "What did the software engineering dept do last year?"

    voyage_client = voyageai.Client()
    query_embedding = voyage_client.embed([query], model="voyage-3-large", input_type="document")
    # Get the actual embedding list (first result)
    query_vec = query_embedding.embeddings[0]

    dsn = get_dsn()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Assuming a common table schema:
            # Table: documents (or embeddings/items/etc.)
            # Columns: id, content (or text), embedding vector(1024)  -- voyage-3 is 1024-dim
            cur.execute("""
                        SELECT id, chunk, embedding <=> %s::vector AS distance
                        FROM rag_chunks
                        ORDER BY embedding <=> %s::vector
                            LIMIT 5;
                        """, (query_vec, query_vec))

            results = cur.fetchall()

            print("Top 3 hits:")
            for row in results:
                print(f"ID: {row[0]}")
                print(f"Content: {row[1]}")
                print(f"Distance (lower is better): {row[2]:.4f}")
                print("---")

if __name__ == "__main__":
    main()
