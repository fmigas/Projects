from src.extractors.model import BaseArticle


class PdfExtractor(BaseArticle):

    def extract(self, file: str) -> dict:
        with open(file, 'r') as f:
            body = f.read()

        pass
