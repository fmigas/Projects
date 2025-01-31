from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from src.config import settings
from src.utils.singular_form import plural_to_singular_english
from src.utils.word_base import base_generator

llm = ChatOpenAI(model = settings.CHAT_ADVANCED, temperature = 0, api_key = settings.OPENAI_API_KEY)


class Translation(BaseModel):
    translation: str = Field(..., title = "Translation of the word or phrase.")


template_translation = """
You are a translator with vast knowledge of human languages. Your will get a word in {target_language} between <<< and >>>. 
Your task is to translate the word between <<< and >>> to {native_language}.
Only respond with the translated word or phrase, don't add any additional text. 


If a word or phrase has multiple meanings, take the context into account. You will find context between ### and ###.

###

{context}

###

<<<

{word}

>>> 

Always respond in {native_language}.
Always translate a word that comes between <<< and >>>, not a word that comes between ### and ###.
"""

# Deliver a reply in Json format "translation": "translated word or phrase".

prompt_first = PromptTemplate.from_template(template_translation)
llm_structured = llm.with_structured_output(Translation)
translate_json_first_step = prompt_first | llm_structured


def get_translation_first_step(word: str, target_language: str, native_language: str, context: str) -> str:
    word = word.strip()
    word = plural_to_singular_english(word)
    base_word = base_generator(word, target_language)
    reply = translate_json_first_step.invoke({"word": base_word, "target_language": target_language, "native_language": native_language, "context": context})
    return {"translation": reply.translation, "base_form": base_word}


class TranslationConfirmed(BaseModel):
    translation: str = Field(..., title = "Translation of the word or phrase.")

template_confirmation = """
You are a translator with vast knowledge of human languages.
Your task is to analyze the translation of the word you have received in a context in which it was used.

Your will get a base form of a word in {target_language} between <<< and >>>.
You will get a translation of the word in {native_language}. It will come between +++ and +++.
You will  get a context in which this word was used. It may come in a different form than the base form. You will find context between ### and ###.
For example a word "dog" may be used in a sentence "These are pretty dogs." or a word "to print" may be used in a sentence "I was printing it.".
You will be given the original word what comes in context between ^^^ and ^^^.

Your task is to analye the translation that comes between *** and ***. If it is correct, return the same translation. If it is incorrect, provide the correct translation.

Only respond with the translated word or phrase, don't add any additional text.
Provide a translation in the same part of speech in which the word was used in the context. For example, if the word was an adjective, provide an adjective in the 
translation.

If a word or phrase has multiple meanings, take the context into account.

###
{context}
###

<<<
{base_word}
>>> 

^^^
{word}
^^^

+++
{translation}
+++

If a word is a noun, always provide a noun in singular form in present time as a translation.
If a word which base form is a very is used as an adjective in the context, provide an adjective in the translation.
Always respond in {native_language}.
If a word in {native_language} is prone to declination, return its base singular form.
"""
# Reply in JSON format, for example 'translation': 'kot'
# Deliver a reply in Json format "translation": "translated word or phrase in singular form".


# Always translate a word that comes between <<< and >>>, not a word that comes between ### and ###.

prompt_confirmation = PromptTemplate.from_template(template_confirmation)
llm_structured = llm.with_structured_output(TranslationConfirmed)
translate_confirmation_chain = prompt_confirmation | llm_structured


def confirm_translation(word: str, base_word: str, translation: str, target_language: str, native_language: str, context: str) -> str:
    reply = translate_confirmation_chain.invoke(
        {"word": word,
         "base_word": base_word,
         "translation": translation,
         "target_language": target_language,
         "native_language": native_language,
         "context": context}
    )
    return reply.translation


def get_translation(word: str, target_language: str, native_language: str, context: str) -> str:
    first_transltion = get_translation_first_step(word = word, target_language = target_language, native_language = native_language, context = context)

    final_translation = confirm_translation(word = word, base_word = first_transltion['base_form'], translation = first_transltion['translation'],
                                            target_language = target_language, native_language = native_language, context = context)

    # correct_translation = base_generator(final_translation, native_language)
    reply = {"translation": final_translation, "base_form": first_transltion['base_form']}

    return reply

# word = "wrinkles"
# context = "He had awful wrinkles around his eyes."
# target_language = "English"
# native_language = "Polish"
# proper_translation = "zmarszczka"
#
# reply = get_translation(word = word, target_language = target_language, native_language = native_language, context = context)
# print(reply)

# final_output = prompt_confirmation.format(
#     word = word,
#     base_word = base_generator(word, target_language),
#     translation = proper_translation,
#     target_language = target_language,
#     native_language = native_language,
#     context = context
# )
#
# print(final_output)
