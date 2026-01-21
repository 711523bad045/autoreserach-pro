from sqlalchemy.orm import Session
from app.database import models
from app.vectorstore.faiss_store import FaissVectorStore, EmbeddingModel


class VectorService:

    vector_store = None
    embedder = EmbeddingModel()

    @staticmethod
    def build_index(db: Session):
        chunks = db.query(models.Chunk).all()

        if not chunks:
            raise Exception("No chunks found in DB. Crawl first.")

        texts = [c.content for c in chunks]
        metadatas = [{"chunk_id": c.id, "page_id": c.page_id} for c in chunks]

        vectors = VectorService.embedder.embed(texts)

        dim = vectors.shape[1]
        store = FaissVectorStore(dim)
        store.add(vectors, texts, metadatas)

        VectorService.vector_store = store

        print(f"FAISS INDEX BUILT WITH {len(texts)} CHUNKS")

    @staticmethod
    def search(query: str, top_k: int = 5):
        if VectorService.vector_store is None:
            raise Exception("Vector index not built yet")

        query_vec = VectorService.embedder.embed([query])
        return VectorService.vector_store.search(query_vec, top_k)
