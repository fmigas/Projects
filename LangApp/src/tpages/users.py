from taipy.gui import Markdown, notify, State
import taipy.gui.builder as tgb
from loguru import logger

from src.utils.users import User
from src.utils.mongo_getters import get_all_documents
from src.config import settings

language_native = ""
language_learned = ""
level = ""
name = ""
userid = ""


def choose_user(state: State):
    state.user = next((u for u in state.users if u['name'] == state.value), None)
    notify(state, 'info', f"User {state.user['name']} selected.")
    state.user_name = state.user['name']
    state.old_words = []  # ! wgrać stare słowa za pomocą funkcji
    state.new_words = []
    state.language_native = state.user['native_language']
    state.language_learned = state.user['learned_language']
    state.level = state.user['level']
    state.userid = state.user['_id']
    state.sentence_1_button = f"Translate sentences from {state.language_learned} to {state.language_native}"
    state.sentence_2_button = f"Translate sentences from {state.language_native} to {state.language_learned}"

    state.all_texts = get_all_documents(settings.MONGODB_DATABASE, "texts")

    state.all_texts = [text for text in state.all_texts if text['user_id'] == str(state.user['_id'])]
    state.all_text_titles = [text['title'] for text in state.all_texts]


def save_user(state: State):
    user = {
        'name': state.name,
        'native_language': state.language_native,
        'learned_language': state.language_learned,
        'level': state.level,
    }
    user = User(**user)
    state.user = user
    state.name = ""
    state.language_native = ""
    state.language_learned = ""
    state.level = ""
    try:
        user.save()
    except ValueError as e:
        notify(state, 'error', str(e))
    notify(state, 'info', f"User {state.user} added and saved.")
    state.users = get_all_documents(settings.MONGODB_DATABASE, "users")
    state.value = state.user.name
    choose_user(state)


with tgb.Page() as user_page:
    with tgb.part("user_selection"):
        tgb.selector(value = "{value}", label = "Choose User", on_change = choose_user, lov = "{user_names}", dropdown = True)
    tgb.html("br")
    tgb.html("br")

    with tgb.part("add_user"):
        tgb.text(value = "Add new user", class_name = "h6")
        tgb.input(value = "{name}", label = "Name")
        tgb.input(value = "{language_native}", label = "Native language")
        tgb.input(value = "{language_learned}", label = "Learned language")
        tgb.selector(value = "{level}", label = "Level", lov = ["A1", "A2", "B1", "B2", "C1", "C2"], dropdown = True, width = "100px")
        tgb.button(label = "Add user", on_action = save_user)


# users_page_ = Markdown("""
# ## Choose User
# <|{value}|selector|lov={user_names}|dropdown|on_change=choose_user|>
#
# User native language: <|{language_native}|>
#
# User learned language: <|{language_learned}|>
# User level: <|{level}|>
# User id: <|{userid}|>
#
# ## Add new user
# Name:  <|{name}|input|placeholder=Enter user name|>
# Native language:  <|{language_native}|input|placeholder=Enter native language|>
# Learned language:  <|{language_learned}|input|placeholder=Enter learned language|>
# Level:  <|{level}|input|placeholder=Enter learned language level|>
# <|button|label=Add user|on_action=save_user|>
#
# """)
