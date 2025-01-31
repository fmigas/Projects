from datetime import datetime, timedelta

from bson import ObjectId
from loguru import logger
from pymongo.errors import OperationFailure

from src.config import settings
from src.utils.mongo_connectors import client


def save_data_to_mongodb(database_name: str, collection_name: str, data: dict | list[dict]):
    """
    Saves data to a specified MongoDB database and collection.
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        if isinstance(data, list):
            result = collection.insert_many(data)
        elif isinstance(data, dict):
            result = collection.insert_one(data)
        else:
            logger.error("Data must be a dictionary or a list of dictionaries")
            return False
        logger.info(f"Data successfully saved to {database_name}.{collection_name}")
        return result
    except OperationFailure as e:
        logger.error(f"Failed to save data: {e}")
        return False


def check_user_exists(name: str):
    # Connect to MongoDB

    # Select the database (adjust 'your_database_name' as needed)
    db = client[settings.MONGODB_DATABASE]

    # Select the 'users' collection
    users_collection = db['users']

    # Check if a user named "Franek" exists
    user = users_collection.find_one({"name": name})

    return user


def update_word_in_mongo(word_id: str, first_seen_false: bool = True, update_ranking: int = None, repetition_date: datetime = None) -> bool:
    try:

        # Get the database
        db = client[settings.MONGODB_DATABASE]

        # Get the collection
        collection = db[settings.MONGODB_COLLECTION_WORDS]

        filter_request = {'_id': ObjectId(word_id)}
        update_request = {}

        if first_seen_false:
            update_request.update({"$set": {"first_seen": False}})

        if update_ranking is not None:
            today = datetime.now()
            today = today.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
            if not repetition_date:
                repetition_date = today + timedelta(days = 1)

            update_request.update({
                "$push": {
                    "ranking": {
                        "date": today,
                        "score": update_ranking
                    }
                }
            })

            update_request.update({
                "$set": {
                    "next_repetition": {
                        "date": repetition_date,
                        "done": False
                    }
                }
            })

        result = collection.update_one(filter = filter_request, update = update_request, upsert = True)

        if result.modified_count > 0:
            logger.info(f"Successfully updated 'first_seen' to False for word_id: {word_id}")
            return True
        else:
            logger.warning(f"No document found with word_id: {word_id}")
            return False

    except OperationFailure as e:
        logger.error(f"Failed to update document: {e}")
    return False

# user_id = '669d1225fead951df71c8a22'
# words = get_words_to_repeate(user_id = user_id, delta_for_tests = 0)
