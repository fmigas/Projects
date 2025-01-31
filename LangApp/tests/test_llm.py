import pytest
from src.llm.generate_sentence import generate_sentence
from src.llm.translate_sentence import translate_sentence
from src.llm.title import generate_title
from src.llm.translate_word import get_translation
from src.llm.rank_translation import get_word_translation_ranking


def test_generate_sentence():
    word = "sister"
    language = "English"
    sentence_A = generate_sentence(word, "A1", language)
    assert isinstance(sentence_A, str)
    assert len(sentence_A) > 0


def test_translate_sentence():
    sentence = "This is a cat."
    level = "A1"
    input_language = "English"
    output_language = "Polish"
    translation = translate_sentence(sentence, level, input_language, output_language)
    assert isinstance(translation, str)
    assert translation == "To jest kot."


def test_generate_title():
    body = "Wlazł kotek na płotek i rozlał mleczko i to koniec bajeczki."
    title = generate_title(body)
    assert isinstance(title, str)
    assert len(title) > 0


def test_get_translation():
    word = "dogs"
    context = "These are pretty dogs."
    target_language = "English"
    native_language = "Polish"
    proper_translation = "pies"
    final_translation = get_translation(word, target_language, native_language, context)
    assert isinstance(final_translation, dict)
    assert final_translation['translation'] == proper_translation
    assert final_translation['base_form'] == "dog"


def test_translation_ranking():
    word_to_translate = "to sit"
    proper_translation = "siedzieć"
    context = "Alice was sitting on the bank by her sister."
    input_language = "English"
    output_language = "Polish"
    your_translation = "biec"

    reply = get_word_translation_ranking(word_to_translate = word_to_translate,
                                         proper_translation = proper_translation,
                                         context = context,
                                         input_language = input_language,
                                         output_language = output_language,
                                         your_translation = your_translation)

    assert isinstance(reply, dict)
    assert reply["rank"] == "3"
    assert reply["source"] == "AI"
