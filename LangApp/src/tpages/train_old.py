from taipy.gui import State, notify
import taipy.gui.builder as tgb
from loguru import logger

from src.utils.mongo_getters import get_words_to_repeate
from src.utils.update_word import update_and_rank_word

words_to_train_old = []
word = {'word': "", 'translation': ""}

your_translation = ""
ranking = ""
finished = ""
translation = ""
submission_number = 0
proper_translation = ""
just_translated_word = ""


# ! KLUCZOWA SPRAWA
# ! Trzeba dla słów, które są dodawane na koniec do ponownej powtórki dodać pole, które sprawi, że nie będzie dla nich wyznaczana nowa data powtórki


def load_old_words(state: State):
    if state.user == "":
        state.finished = "User not selected!"
        notify(state, 'error', f"User not selected.")
    else:
        # ? pobranie wszystkich słów dla danego usera z niezrobioną powtórką
        state.words_to_train_old = get_words_to_repeate(
            user_id = state.user['_id'],
            delta_for_tests = 0)

        if len(state.words_to_train_old) > 0:
            logger.info(f"Words to train: {[word['word'] for word in state.words_to_train_old]}")
            state.word = state.words_to_train_old[0]
            state.words_to_train_old = state.words_to_train_old[1:]
            state.submission_number = 1
        else:
            state.finished = "No words to train!"
            state.words_to_train_old = [""]
            state.word = {'word': "", 'translation': ""}


def on_submission(state):
    if state.submission_number == 1:
        state.translation = state.your_translation
        if state.your_translation == "":
            state.translation = ""
        state.your_translation = ""
        state.just_translated_word = state.word['word']

        state.ranking, state.proper_translation = update_and_rank_word(state.word, state.translation, state.text_body, calculate_next_repetition = True)

        if state.ranking > 1:
            state.word['word_retrained'] = True
            state.words_to_train_old.append(dict(state.word))  # ! te słowa nie powinny mieć nowej daty powtórki

        state.word = state.words_to_train_old[0]
        state.words_to_train_old = state.words_to_train_old[1:]

        state.submission_number = 2
        print(state.words_to_train_old)

    else:

        if len(state.words_to_train_old) > 0:
            state.translation = state.your_translation
            if state.your_translation == "":
                state.translation = " "
            state.your_translation = ""
            state.just_translated_word = state.word['word']

            state.ranking, state.proper_translation = update_and_rank_word(state.word, state.translation, state.text_body, calculate_next_repetition = True)

            if state.ranking > 1:
                state.word['word_retrained'] = True
                state.words_to_train_old.append(dict(state.word))  # ! te słowa nie powinny mieć nowej daty powtórki

            state.word = state.words_to_train_old[0]
            state.words_to_train_old = state.words_to_train_old[1:]
        else:
            state.translation = state.your_translation
            if state.your_translation == "":
                state.translation = " "
            state.your_translation = ""
            state.just_translated_word = state.word['word']

            if 'word_id' in state.word:
                state.ranking, state.proper_translation = update_and_rank_word(state.word, state.translation, state.text_body, calculate_next_repetition = True)
                if state.ranking > 1:
                    state.word['word_retrained'] = True
                    state.words_to_train_old.append(dict(state.word))  # ! te słowa nie powinny mieć nowej daty powtórki
                    state.word = state.words_to_train_old[0]
                    state.words_to_train_old = state.words_to_train_old[1:]
                else:
                    state.finished = "No words to train!"
                    state.words_to_train_old = []
                    state.word = {'word': "", 'translation': ""}
                    state.your_translation = ""


with tgb.Page() as repetitions_page:
    with tgb.layout(columns = "1 4", columns__mobile = "1", class_name = "repetition_page"):
        # First map part
        with tgb.part("train_words_sidebar"):
            tgb.button("Repeate words", on_action = load_old_words, class_name = "train_old_button")

        # Second map part
        with tgb.part():
            # tgb.text(value = "Word to translate: {word['word']}")
            with tgb.layout(columns = "150px 4", class_name = "word_to_translate_box"):
                tgb.text(value = "Word to translate:", class_name = "text-small")
                # tgb.text(value = "{word['word']}", class_name = "word_to_translate")
                tgb.text(value = "{word['word']}", class_name = "text-weight800 text-uppercase")
            tgb.input(value = "{your_translation}", on_action = on_submission, class_name = "old_input fullwidth")
            # tgb.text("Correct translation is: {proper_translation}.")
            with tgb.layout(columns = "170px 1 4", class_name = "correct_translation_box"):
                tgb.text(value = "Correct translation for:", class_name = "text-small")
                tgb.text(value = "{just_translated_word}")
                tgb.text(value = "{proper_translation}", class_name = "text-weight800 text-uppercase")

            with tgb.layout(columns = "150px 4", class_name = "ranking_box"):
                tgb.text(value = "Translation ranked:", class_name = "text-small")
                tgb.text(value = "{ranking}")

            tgb.text("{finished}", class_name = "finished_text text-small")

#
# with tgb.Page() as repetitions_page:
#     tgb.button("Repeate words", on_action = load_old_words, class_name = "train_button")
#     # tgb.text("Words to repeat today : {words_to_train_old}")
#     tgb.text("Word to translate: {word['word']}")
#     tgb.input("{your_translation}", label = "Your translation", on_action = on_submission, class_name = "fullwidth")
#     # tgb.text("Correct translation is: {proper_translation}.")
#     tgb.text(value = "Correct translation is: {proper_translation}", class_name = "correct_translation")
#     tgb.text("Translation ranked: {ranking}")
#     tgb.text("{finished}")


"""
Mechanizm z word['word_retrained'] działa, ale lepiej zmienić to w ten sposób, że
1. next_repetition jest ustalane na kolejny dzień na etapie dodawania słówka do bazy w text.py
2. w tej sytuacji flaga next_repetition = None powinna skutkować w funkcji update_word_in_mongo tym, update_request w ogóle nie ma informacji o 
repetition_date;
czyli repetition_date jest aktualizowane tylko przy train_old przy pierwszym powtórzeniu słówka
"""
