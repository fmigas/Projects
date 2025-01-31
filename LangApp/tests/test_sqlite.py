from src.utils.sqlite_db import get_words_from_sqlite_by_sessionid, save_word_to_database

import random
import string


def test_sqlite():
    word = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    sessionid = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))

    save_word_to_database(word, sessionid)
    words = get_words_from_sqlite_by_sessionid(sessionid = sessionid)
    assert isinstance(words, list)
    assert word in words
