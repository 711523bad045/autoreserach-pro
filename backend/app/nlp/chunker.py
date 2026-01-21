class TextChunker:

    @staticmethod
    def chunk_text(text: str, max_chars: int = 1000):
        chunks = []
        start = 0

        text_length = len(text)

        while start < text_length:
            end = start + max_chars
            chunk = text[start:end]
            chunks.append(chunk)
            start = end

        return chunks
