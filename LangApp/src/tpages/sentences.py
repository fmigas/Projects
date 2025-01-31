"""
1. download words from monbodb by userid with text_id - DONE

2. na podstawie text_id ściągnąć tekst i generować zdania z użyciem kontekstu, w którym były użyte
ewentualnie user może definiować tematykę, która go interesuje (np. finansowa)

3. generate sentences and their translations based on the selected words by user level - DONE

train translations
"""
from taipy.gui import State, notify
import taipy.gui.builder as tgb
from loguru import logger

from src.utils.mongo_getters import load_words
from src.llm import generate_sentence, translate_sentence

sentence = ""
translation = ""
next_sentence = ""
next_translation = ""
proper_translation = ""
your_translation = ""
your_printed_translation = ""
finished = ""

learned_language = ""
native_language = ""

words = []
all_words = []


def get_sentence_and_translation(word: str, user: dict, learned_language: str, native_language: str):
    """
    Ta funkcja generuje zdanie i jego tłumaczenie na podstawie słowa i usera.

    :param word:
    :param user:
    :return:
    """
    logger.info(f"Sentence in {learned_language} and translation in {native_language} for word {word}")
    sentence = generate_sentence(
        word = word,
        # level = user['level'],
        level = "A2",
        # language = user['learned_language']
        language = learned_language
    )

    translation = translate_sentence(
        sentence = sentence,
        # level = user['level'],
        level = "A2",
        # input_language = user['learned_language'],
        input_language = learned_language,
        # output_language = user['native_language']
        output_language = native_language
    )

    return sentence, translation


def load_words_to_sentences(state: State, sentences_language: str):
    """
    Ta funkcja pobiera słowa dla danego usera.

    :param state:
    :return:
    """
    state.your_translation = ""
    state.your_printed_translation = ""
    state.proper_translation = ""
    state.sentence = ""

    match sentences_language:
        case 'learned':
            state.learned_language = state.user['learned_language']
            state.native_language = state.user['native_language']

        case 'native':
            state.learned_language = state.user['native_language']
            state.native_language = state.user['learned_language']

    if state.user == "":
        state.finished = "User not selected!"
        notify(state, 'error', f"User not selected.")
    else:
        collection = "words"
        shuffle = False
        words = load_words(
            collection = collection,
            user_id = state.user['_id'],
            shuffle = shuffle)
        notify(state, 'info', f"Words downloaded. Generating sentences and translations.")

        match sentences_language:
            case 'learned':
                state.words = [word['word'] for word in words]
            case 'native':
                state.words = [word['translation'] for word in words]
            case _:
                state.words = [word['word'] for word in words]

        state.words = list(set(state.words))
        state.all_words = state.words

        if len(state.words) > 0:
            state.sentence, state.translation = get_sentence_and_translation(
                word = state.words[0],
                user = state.user,
                learned_language = state.learned_language,
                native_language = state.native_language
            )

            if len(state.words) > 1:
                state.words = state.words[1:]
                state.next_sentence, state.next_translation = get_sentence_and_translation(
                    word = state.words[0],
                    user = state.user,
                    learned_language = state.learned_language,
                    native_language = state.native_language,
                )
            else:
                state.words = []

        else:
            state.finished = "No sentences to translate!"
            notify(state, 'error', f"No sentences to translate.")


def load_words_learned_language(state: State):
    load_words_to_sentences(state, sentences_language = 'learned')


def load_words_native_language(state: State):
    load_words_to_sentences(state, sentences_language = 'native')


def on_submission(state: State):
    if state.words:
        state.proper_translation = state.translation
        state.your_printed_translation = state.your_translation
        state.your_translation = ""
        state.sentence, state.translation = state.next_sentence, state.next_translation

        state.words = state.words[1:]
        if state.words:
            # logger.info(f"Learned language: {state.learned_language}, native language: {state.native_language}")
            state.next_sentence, state.next_translation = get_sentence_and_translation(word = state.words[0],
                                                                                       user = state.user,
                                                                                       learned_language = state.learned_language,
                                                                                       native_language = state.native_language)

    else:
        state.proper_translation = state.translation
        state.your_printed_translation = state.your_translation
        state.your_translation = ""
        state.sentence = ""
        state.finished = "No more sentences to translate!"


with tgb.Page() as sentences_page:
    with tgb.layout(columns = "1 1", columns__mobile = "1"):
        tgb.button(label = "{sentence_1_button}", on_action = load_words_learned_language,
                   class_name = "sentences")

        tgb.button(label = "{sentence_2_button}", on_action = load_words_native_language,
                   class_name = "sentences")

    tgb.html("br")

    with tgb.part("sentences_content"):
        tgb.text(value = "{sentence}", class_name = "sentence_to_translate_box")
        tgb.input(value = "{your_translation}", label = "Your translation", on_action = on_submission, class_name = "fullwidth old_input")

    with tgb.part("replies_content"):
        with tgb.layout(columns = "170px 4", columns__mobile = "1"):
            tgb.text("Your translation:", class_name = "text-small")
            tgb.text("{your_printed_translation}")
        with tgb.layout(columns = "170px 4", columns__mobile = "1"):
            tgb.text("Correct translation:", class_name = "text-small")
            tgb.text("{proper_translation}")

        tgb.text("{finished}")
