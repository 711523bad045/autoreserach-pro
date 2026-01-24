import numpy as np
import faiss
from typing import List

class VectorService:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add_embeddings(self, embeddings: List[List[float]], texts: List[str]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.texts.extend(texts)

    def query(self, query_embedding: List[float], top_k: int = 5):
        q = np.array([query_embedding]).astype("float32")
        dist, ids = self.index.search(q, top_k)
        return [self.texts[i] for i in ids[0]]
