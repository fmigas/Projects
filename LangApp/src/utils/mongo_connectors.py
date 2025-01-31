from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from loguru import logger

from src.config import settings

uri = f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@learning.safgfdd.mongodb.net/?retryWrites=true&w=majority&appName={settings.MONGODB_CLUSTER_NAME}"


def connect_to_mongodb():
    try:
        client_ = MongoClient(uri)
        client_.admin.command('ping')  # Check if the connection is successful
        logger.info("Successfully connected to MongoDB")
        return client_
    except ConnectionFailure:
        logger.error("Failed to connect to MongoDB")
        return None


client = connect_to_mongodb()
