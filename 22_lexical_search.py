#! /usr/bin/env python

# https://medium.com/@kimdoil1211/bm25-for-developers-a-guide-to-smarter-keyword-search-e6d83e8c8c8c
import bm25s
import re
import Stemmer  # optional: for stemming

# Chunk by section
def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)


def main():

    with open("./rag_input.md", "r") as f:
        text = f.read()

    corpus = chunk_by_section(text)

    # optional: create a stemmer
    stemmer = Stemmer.Stemmer("english")

    # Tokenize the corpus and only keep the ids (faster and saves memory)
    corpus_tokens = bm25s.tokenize(corpus, stopwords="en", stemmer=stemmer)

    # Create the BM25 model and index the corpus
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    # Query the corpus
    query = "What happened with INC-2023-Q4-011?"
    query_tokens = bm25s.tokenize(query, stemmer=stemmer)

    # Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k).
    # To return docs instead of IDs, set the `corpus=corpus` parameter.
    results, scores = retriever.retrieve(query_tokens, k=3)

    for i in range(results.shape[1]):
        idx, score = results[0, i], scores[0, i]
        print(f"Rank {i + 1} (score: {score:.2f}): {idx}")
        print(corpus[idx])
        print()

if __name__ == "__main__":
    main()
