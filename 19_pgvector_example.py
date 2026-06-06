#! /usr/bin/env python
from dotenv import load_dotenv
load_dotenv()
import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from os import getenv

# Connect (adjust credentials)
conn = psycopg.connect(
    dbname=getenv("POSTGRES_DB_NAME"), 
    user=getenv("POSTGRES_USER"),
    password=getenv("POSTGRES_PASSWD"),
    host="localhost"
)

# Register vector type support
register_vector(conn)

with conn.cursor() as cur:
    # Enable extension (if not already)
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print(cur.execute("SELECT current_database();"))

    # Create table
    cur.execute(""" CREATE TABLE IF NOT EXISTS test_items
                ( id SERIAL PRIMARY KEY, content TEXT, embedding vector( 3 )); """)

    # Insert sample data
    embedding = np.array([1.0, 2.0, 3.0])
    cur.execute(
        "INSERT INTO test_items (content, embedding) VALUES (%s, %s)",
        ("Example item", embedding)
    )

    # Query nearest neighbors (cosine similarity example)
    query_embedding = np.array([1.1, 2.1, 3.0])
    # <=> is cosine distance in pgvector
    cur.execute("""
                SELECT id, content, embedding
                FROM test_items
                ORDER BY embedding <=> %s
                    LIMIT 5;
                """, (query_embedding,))

    results = cur.fetchall()
    for row in results:
        print(row)

conn.commit()
conn.close()