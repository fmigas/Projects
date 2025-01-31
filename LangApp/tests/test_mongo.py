from src.utils.mongo_getters import get_all_documents
from src.config import settings


def test_mongo_connection():
    from src.utils.mongo_connectors import client
    assert client is not None


def test_get_all_documents():
    users = get_all_documents(settings.MONGODB_DATABASE, "users")
    words = get_all_documents(settings.MONGODB_DATABASE, "words")
    assert isinstance(users, list)
    assert isinstance(words, list)
