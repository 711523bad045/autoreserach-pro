from app.database.models import Chunk


class VectorService:
    @staticmethod
    def build_index(db, limit: int = 12):
        """
        Returns latest chunks from DB.
        This is intentionally SIMPLE and FAST.
        No joins, no embeddings, no heavy logic.
        """

        return (
            db.query(Chunk)
            .order_by(Chunk.id.desc())
            .limit(limit)
            .all()
        )
