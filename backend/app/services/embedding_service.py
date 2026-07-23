from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def build_index(self, texts):

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )

        index = faiss.IndexFlatL2(
            embeddings.shape[1]
        )

        index.add(embeddings)

        return index, embeddings

    def search(
        self,
        query,
        texts,
        index,
        k=5
    ):

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        distances, ids = index.search(
            query_embedding,
            k
        )

        return [
            texts[i]
            for i in ids[0]
        ]