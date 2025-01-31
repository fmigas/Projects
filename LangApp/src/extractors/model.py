from pydantic import BaseModel
from abc import ABC, abstractmethod


class BaseArticle(BaseModel, ABC):
    user_id: str
    title: str = None
    original_text: str = None  # pełny tekst
    cleaned_text: str = None  # tekst po usunięciu stop words i prostych words za pomocą funkcji llm/words/clean_text
    words_with_context: list[dict] = None  # lista słów z kontekstem

    def to_mongo(self, **kwargs):
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset = exclude_unset,
            by_alias = by_alias,
            **kwargs,
        )

        if "_id" not in parsed and 'id' in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed

    @abstractmethod
    def extract(self, **kwargs) -> None:
        pass
