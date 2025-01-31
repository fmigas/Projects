from taipy.gui import Gui, State


from src.tpages import (
    user_page,
    text_page,
    first_seen_training,
    repetitions_page,
    sentences_page,
    root,
)
from src.config import settings
from src.utils.mongo_getters import get_all_documents
from extensions.example_library import ExampleLibrary


value = ""
user = ""
user_name = ""
users = get_all_documents(settings.MONGODB_DATABASE, "users")
all_texts = None
all_text_titles = None

user_names = [user['name'] for user in users]
text = ""
old_words = []
new_words = []
text = ""
text_title = ""
text_body = ""
sessionid = " "
sentence_1_button = ""
sentence_2_button = ""


def on_init(state: State) -> None:
    state.user_names = user_names
    state.users = users
    state.user = user
    state.user_name = user_name
    state.value = value
    state.old_words = old_words
    state.new_words = new_words
    state.all_texts = all_texts
    state.all_text_titles = all_text_titles
    state.text = text
    state.text_title = text_title
    state.text_body = text_body
    state.sessionid = sessionid
    state.sentence_1_button = sentence_1_button
    state.sentence_2_button = sentence_2_button

pages = {
    "/": root,
    "users": user_page,
    "text": text_page,
    "new_words": first_seen_training,
    "old_words": repetitions_page,
    "sentences": sentences_page
}

if __name__ == "__main__":
    Gui(pages = pages, libraries = [ExampleLibrary()]).run(host = '0.0.0.0', port = 5002, dark_mode = False, use_reloader = True)
