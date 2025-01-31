import pytest

from src.utils.singular_form import plural_to_singular_english
from src.utils.word_base import base_generator


def test_plural_to_singular():
    plural_word = "conversations"
    singular_word = plural_to_singular_english(plural_word)
    assert singular_word == "conversation"

    plural_word = "dogs"
    singular_word = plural_to_singular_english(plural_word)
    assert singular_word == "dog"


def test_base_generator():
    word = "conversations"
    lang = "English"
    base = base_generator(word, lang)
    assert base == "conversation"

    word = "kota"
    lang = "Polish"
    base = base_generator(word, lang)
    assert base == "kot"
