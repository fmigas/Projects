from src.extractors.text import TextExtractor
from src.extractors.operator import Operator
from src.extractors.model import BaseArticle
from src.extractors.url import UrlExtractor

operator = Operator()
operator.register_model(model = TextExtractor, marker = 'txt')
operator.register_model(model = UrlExtractor, marker = 'http')
valid_models = operator.registered_models


def generate_content(file: str, user_id: str, **kwargs) -> BaseArticle:
    if file.strip()[:4] == 'http':
        model = operator.get_model(marker = 'http')
    else:
        if file.split('.')[-1] not in valid_models:
            raise ValueError(f"Invalid file type. Must be one of: {', '.join(valid_models)}")
        model = operator.get_model(file.split('.')[-1])

    extractor = model(user_id = user_id)

    text = extractor.extract(file = file, **kwargs)

    return text
