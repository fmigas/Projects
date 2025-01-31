from taipy.gui import Markdown, notify, State
import random
import string
from loguru import logger

from src.utils.mongo_functions import save_data_to_mongodb
from src.utils.mongo_getters import get_all_documents
from src.utils.sqlite_db import get_words_from_sqlite_by_sessionid
from src.extractors import generate_content
from src.llm.translate_word import get_translation
from src.config import settings


selected_words = []
text_body = " "
content = " "
all_translations = {"words": [], "base_forms": [], "translations": []}
table_words = []
table_base_forms = []
table_translations = []


def choose_text(state: State) -> None:
    if '_id' not in state.user:
        notify(state, 'error', "User not selected.")
        return

    state.text = next((t for t in state.all_texts if t['title'] == state.text_title), None)
    state.text_body = state.text['original_text']
    state.sessionid = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
    logger.info(f"Text {state.text['title']} selected.")
    logger.info(f"Sessionid: {state.sessionid}")
    notify(state, 'info', f"Text {state.text['title']} selected.")
    state.all_translations = {"words": [], "base_forms": [], "translations": []}


def save_file(state: State) -> None:
    if '_id' not in state.user:
        notify(state, 'error', "User not selected.")
        return

    state.text = generate_content(file = state.content, user_id = state.user['_id'], learned_language = state.user['learned_language'])
    data = {
        'title': state.text['title'],
        'original_text': state.text['original_text'],
        'user_id': state.user['_id'],
    }

    save_result = save_data_to_mongodb(
        database_name = settings.MONGODB_DATABASE,
        collection_name = settings.MONGODB_COLLECTION_TEXTS,
        data = data
    )
    state.content = ""

    if save_result:
        notify(state, 'success', f"Text {state.text['title']} saved to database.")
        state.all_texts = get_all_documents(settings.MONGODB_DATABASE, "texts")
        state.all_texts = [text for text in state.all_texts if text['user_id'] == str(state.user['_id'])]
        state.all_text_titles = [text['title'] for text in state.all_texts]
    else:
        notify(state, 'error', f"Error saving text {state.text['title']} to database.")


def translate_words(state: State):
    if state.user == "":
        state.finished = "User not selected!"
        notify(state, 'error', f"User not selected.")
    else:
        state.selected_words = get_words_from_sqlite_by_sessionid(state.sessionid)
        logger.info(f"Sessionid: {state.sessionid}")
        logger.info(f"Selected words: {state.selected_words}")
        # logger.info(f"User: {state.user}")

        # logger.debug(f"All words in sqlite for session {state.sessionid}: {get_words_from_sqlite_by_sessionid(state.sessionid)}")

        all_to_mongo = []
        for word in state.selected_words:
            reply = get_translation(word = word,
                                    target_language = state.user['learned_language'],
                                    native_language = state.user['native_language'],
                                    context = state.text_body, )

            translation = reply.get("translation")
            base_form = reply.get("base_form")
            table_words.append(word)
            table_base_forms.append(base_form)
            table_translations.append(translation)

            all_to_mongo.append({'word': word,
                                 'base_form': base_form,
                                 'translation': translation,
                                 'user_id': str(state.user['_id']),
                                 'text_id': str(state.text['_id']),
                                 'learned_language': state.user['learned_language'],
                                 'native_language': state.user['native_language'],
                                 'first_seen': True,
                                 'sessionid': state.sessionid,
                                 })

        all_translations = {"words": table_words, "base_forms": table_base_forms, "translations": table_translations}

        state.all_translations = all_translations

        save_data_to_mongodb(database_name = settings.MONGODB_DATABASE, collection_name = settings.MONGODB_COLLECTION_WORDS, data = all_to_mongo)


text_page = Markdown("""
Load text from file
<|{content}|file_selector|label=Select File|on_action=save_file|extensions=.txt,.pdf,.docx|drop_message=Drop Message|>

Load text from URL
<|{content}|input|on_action=save_file|class_name=fullwidth|>

Choose Text
<|{text_title}|selector|lov={all_text_titles}|dropdown|on_change=choose_text|>

<|{text_body}|example.label|sessionid={sessionid}|>

<|button|label=Translate selected words|on_action=translate_words|class_name=sentences|>

<|{all_translations}|table|>

""")


# with tgb.Page() as text_page:
#     tgb.button("Load new text", on_action = save_file)
#     tgb.text("Choose text to translate")
#     tgb.selector("Text title", lov = all_text_titles, dropdown = True, on_change = choose_text)
#     tgb.example.label(f"{text_body}", sessionid = {sessionid})
#     tgb.button("Translate selected words", on_action = translate_words)
