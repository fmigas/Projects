from taipy.gui import State, notify
import taipy.gui.builder as tgb

from src.utils.mongo_getters import get_words_by_user_from_words_collection
from src.utils.update_word import update_and_rank_word
from src.config import settings

words_to_train_new = []
word = {'word': "", 'translation': ""}

your_translation = ""
ranking = ""
finished = ""
translation = ""
submission_number = 0
proper_translation = ""
just_translated_word = ""


def train_new_words(state: State):
    if state.user == "":
        # state.finished = "User not selected!"
        notify(state, 'error', f"User not selected.")
    else:
        state.words_to_train_new = get_words_by_user_from_words_collection(database_name = settings.MONGODB_DATABASE,
                                                                           collection_name = settings.MONGODB_COLLECTION_WORDS,
                                                                           user_id = state.user['_id'],
                                                                           text_id = state.text['_id'],
                                                                           first_seen = True,
                                                                           sessionid = state.sessionid)

        if len(state.words_to_train_new) > 0:
            state.word = state.words_to_train_new[0]
            state.words_to_train_new = state.words_to_train_new[1:]
            state.submission_number = 1
        else:
            state.finished = "No words to train!"
            state.words_to_train_new = [""]
            state.word = {'word': "", 'translation': ""}


def on_submission(state):
    if state.submission_number == 1:
        state.translation = state.your_translation
        if state.your_translation == "":
            state.translation = " "
        state.your_translation = ""
        state.just_translated_word = state.word['word']

        state.ranking, state.proper_translation = update_and_rank_word(state.word, state.translation, state.text_body)

        if state.ranking > 1:
            state.words_to_train_new.append(dict(state.word))

        state.word = state.words_to_train_new[0]
        state.words_to_train_new = state.words_to_train_new[1:]

        state.submission_number = 2
        print(state.words_to_train_new)

    else:

        if len(state.words_to_train_new) > 0:
            state.translation = state.your_translation
            if state.your_translation == "":
                state.translation = " "
            state.your_translation = ""
            state.just_translated_word = state.word['word']

            state.ranking, state.proper_translation = update_and_rank_word(state.word, state.translation, state.text_body)

            if state.ranking > 1:
                state.words_to_train_new.append(dict(state.word))

            state.word = state.words_to_train_new[0]
            state.words_to_train_new = state.words_to_train_new[1:]
        else:
            state.translation = state.your_translation
            if state.your_translation == "":
                state.translation = " "
            state.your_translation = ""
            state.just_translated_word = state.word['word']

            if 'word_id' in state.word:
                state.ranking, state.proper_translation = update_and_rank_word(state.word, state.translation, state.text_body)
                if state.ranking > 1:
                    state.words_to_train_new.append(dict(state.word))
                    state.word = state.words_to_train_new[0]
                    state.words_to_train_new = state.words_to_train_new[1:]
                else:
                    state.finished = "No words to train!"
                    state.words_to_train_new = []
                    state.word = {'word': "", 'translation': ""}
                    state.your_translation = ""

with tgb.Page() as first_seen_training:
    with tgb.layout(columns = "1 4", columns__mobile = "1", class_name = "repetition_page"):
        # First map part
        with tgb.part("train_words_sidebar"):
            tgb.button("Learn words", on_action = train_new_words, class_name = "train_old_button")

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




