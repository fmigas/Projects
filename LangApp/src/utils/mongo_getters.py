import random
from datetime import datetime, timedelta

from bson import ObjectId
from loguru import logger
from pymongo.errors import OperationFailure

from src.config import settings
from src.utils.mongo_connectors import client


def get_all_documents(database_name: str, collection_name: str):
    """
    Retrieves all documents from a specified MongoDB collection.

    Args:
    client (pymongo.MongoClient): MongoDB client object
    database_name (str): Name of the database
    collection_name (str): Name of the collection (default is "users")

    Returns:
    list: A list of all documents in the collection
    None: If an error occurs during the operation
    """
    try:
        # Get the database
        # client = connect_to_mongodb()
        db = client[database_name]

        # Get the collection
        collection = db[collection_name]

        # Retrieve all documents
        documents = list(collection.find({}))

        # close_mongodb_connection(client)
        documents = [convert_id_to_string(doc) for doc in documents]

        return documents

    except OperationFailure as e:
        return None


def get_words_by_user_from_words_collection(database_name: str, collection_name: str, user_id: str, text_id: str = None, first_seen: bool = None, sessionid: str = None):
    query = {"user_id": str(user_id)}

    if text_id is not None:
        query["text_id"] = str(text_id)

    if first_seen is not None:
        query["first_seen"] = first_seen

    if sessionid is not None:
        query["sessionid"] = str(sessionid)

    try:
        # Get the database
        db = client[database_name]

        # Get the collection
        collection = db[collection_name]

        # Retrieve records and extract the 'word_base' field
        all_words = []
        for record in collection.find(query):
            word_id = str(record['_id'])
            word_base = record.get('base_form')
            translation = record.get('translation')
            # context = record.get('context')
            learned_language = record.get('learned_language')
            native_language = record.get('native_language')
            text_id = record.get('text_id')
            if word_base:  # Ensure word_base exists
                all_words.append(
                    {'word': word_base, 'translation': translation, 'learned_language': learned_language, 'native_language': native_language, 'word_id': word_id,
                     'text_id': text_id})

        return all_words

    except OperationFailure as e:
        return None


def load_words(collection: str, user_id: str, shuffle: bool = False) -> list[dict]:
    logger.info(f"Mongo database: {settings.MONGODB_DATABASE}, collection: {collection}, user_id: {user_id}")
    match collection:
        case "words":
            all_words = get_words_by_user_from_words_collection(settings.MONGODB_DATABASE, "words", user_id)
        # case "words_ranking":
        #     all_words = get_words_by_user_from_words_ranking_collection(settings.MONGODB_DATABASE, "words_ranking", user_id)
        case _:
            raise ValueError("Invalid collection name")

    if shuffle:
        random.shuffle(all_words)
    return all_words


def get_words_by_ids(database_name: str, collection_name: str, ids: list[str]):
    try:
        # Get the database
        # client = connect_to_mongodb()
        db = client[database_name]

        # Get the collection
        collection = db[collection_name]

        all_words = []
        for id in ids:
            record = collection.find_one({"_id": ObjectId(id)})

            word_id = str(record['_id'])
            word_base = record.get('base_form')
            translation = record.get('translation')
            context = record.get('context')
            learned_language = record.get('learned_language')
            native_language = record.get('native_language')
            if word_base:  # Ensure word_base exists
                all_words.append({'word': word_base, 'translation': translation, 'context': context, 'learned_language': learned_language, 'native_language':
                    native_language, 'word_id': word_id})

        return all_words

    except OperationFailure as e:
        return None


def get_words_to_repeate(user_id: str, delta_for_tests: int = 0):
    """
    Pobiera słowa z kolekcji "words" dla danego usera z next_repetition.date z datą dzisiejszą lub wcześniejszą i next_repetition.done = False

    :param user_id:
    :param delta_for_tests: domyślnie 0 (czyli pobiera dane z dnia dzisiejszego i wcześniej), ale do testów można też wziąć późniejsze dni
    :return:
    """

    db = client[settings.MONGODB_DATABASE]
    collection = db[settings.MONGODB_COLLECTION_WORDS]
    # Set the current date to the start of the day
    today = datetime.now() + timedelta(days = delta_for_tests)
    today = today.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

    # Query to retrieve records
    query = {
        'next_repetition.date': {'$lte': today},  # Get dates today or earlier
        'next_repetition.done': False,  # done is false
        'user_id': str(user_id)
    }

    # Execute the query
    # results = list(collection.find(query))

    all_words = []
    for record in collection.find(query):
        word_id = str(record['_id'])
        word_base = record.get('base_form')
        translation = record.get('translation')
        # context = record.get('context')
        learned_language = record.get('learned_language')
        native_language = record.get('native_language')
        text_id = record.get('text_id')
        ranking = record.get('ranking')
        if word_base:  # Ensure word_base exists
            all_words.append(
                {'word': word_base, 'translation': translation, 'learned_language': learned_language, 'native_language': native_language, 'word_id': word_id,
                 'text_id': text_id, 'ranking': ranking})

    return all_words


def convert_id_to_string(record):
    """
    Converts the _id field of a MongoDB record from ObjectId to string.

    Parameters:
    record (dict): A MongoDB record represented as a dictionary.

    Returns:
    dict: The record with _id converted to string.
    """
    # Check if the record has an '_id' field and if it's an ObjectId
    if '_id' in record and isinstance(record['_id'], ObjectId):
        record['_id'] = str(record['_id'])

    return record
