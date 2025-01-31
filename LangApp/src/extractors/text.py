from unstructured.cleaners.core import (
    clean,
    clean_non_ascii_chars,
    replace_unicode_quotes,
)

from src.extractors.model import BaseArticle
from src.llm.title import generate_title
from src.extractors.extractor_utils import remove_excess_newlines


class TextExtractor(BaseArticle):

    def extract(self, file: str, **kwargs) -> dict:
        with open(file, 'r') as f:
            body = f.read()

        body = clean(text = body, lowercase = False, extra_whitespace = False, dashes = True, bullets = True)
        body = remove_excess_newlines(body)
        body = clean_non_ascii_chars(body)
        body = replace_unicode_quotes(body)

        self.original_text = body.strip()
        self.title = generate_title(body = body)

        return self.to_mongo()
