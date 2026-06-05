#! /usr/bin/env python
# Chunk by a set number of charactesr
import re
from dotenv import load_dotenv
import voyageai

from vector_index import VectorIndex

load_dotenv()

# some clunker of an idea
def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunk_text = text[start_idx:end_idx]
        chunks.append(chunk_text)
        start_idx =  end_idx - chunk_overlap if end_idx < len(text) else len(text)
    return chunks

# Chunk by section
def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)

# Embedding Generation
def generate_embedding(client, input, model="voyage-3-large", input_type="query"):
    if not (input_is_list:=isinstance(input, list)): input = [input]
    result = client.embed(input, model=model, input_type=input_type)
    return  result.embeddings if input_is_list else  result.embeddings[0]

def main():
    with open("./rag_input.md", "r") as f:
        text = f.read()

    chunks = chunk_by_section(text)
    # for chunk in chunks[:3]: print(chunk + "\n----\n")
    voyage_client = voyageai.Client()
    # a test
    # embedding = generate_embedding(voyage_client, chunks[0])
    # print(chunks[0][:10], embedding)

    # 2 . Generate embeddings for all chunks at once
    embeddings = generate_embedding(voyage_client, chunks)

    # 3. Create a vector store and add each embedding to it
    # Note: converted to a bulk operation to avoid rate limiting errors from VoyageAI
    store = VectorIndex()
    for embedding, chunk in zip(embeddings, chunks):
        store.add_vector(embedding, {"content": chunk})

    # $. Generate embedding for the user query
    user_embedding = generate_embedding(voyage_client, "What did the software engineering dept do last year?")

    # 6. Find relevant content
    results = store.search(user_embedding, 2)

    for doc, distance in results:
        print(distance, "\n", doc["content"][0:200], "\n")


if __name__ == "__main__":

    main()
