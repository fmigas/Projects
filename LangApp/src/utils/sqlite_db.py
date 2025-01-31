import requests
from loguru import logger
from sqlalchemy.testing.plugin.plugin_base import config
import json

from src.config import settings


def get_words_from_sqlite_by_sessionid(sessionid: str = None) -> list[dict]:
    params = {
        "sessionId": sessionid
    }

    try:
        # Send GET request with parameters
        response = requests.get(settings.SQLITE_DATABASE, params = params)

        # Check if the request was successful
        if response.status_code == 200:
            words = response.json()
            words = words.get("words", [])
            if not words:
                print("No words found")
                return []
            words = [x['word'] for x in words]
            return words
        else:
            print(f"Failed to retrieve words. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

# words = get_words_from_sqlite_by_sessionid()
# logger.info(f"Words retrieved {words}")


def save_word_to_database(word: str, id: str) -> None:
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'sessionId': id,
            'word': word,
        }

        address = settings.SQLITE_DATABASE

        response = requests.post(address, headers = headers, data = json.dumps(payload))

        if response.status_code != 200:
            raise Exception('Failed to save word')
            return response

        # data = response.json()  # Optional: Get response data if needed
        # print('Word saved successfully:', data)
        return response

    except Exception as error:
        print('Error saving word:', error)
        return response

