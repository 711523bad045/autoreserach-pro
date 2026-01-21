import re


class Cleaner:

    @staticmethod
    def clean(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()
