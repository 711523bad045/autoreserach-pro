import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class FaissVectorStore:

    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []
        self.metadatas = []

    def add(self, vectors: np.ndarray, texts: list[str], metadatas: list[dict]):
        self.index.add(vectors)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        D, I = self.index.search(query_vector, top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.texts):
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadatas[idx]
                })
        return results


class EmbeddingModel:

    def __init__(self):
        # Downloads once, then works offline
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, show_progress_bar=False)
        return np.array(vectors).astype("float32")
