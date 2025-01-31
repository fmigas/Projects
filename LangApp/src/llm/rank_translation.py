from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from src.utils.word_base import base_generator
from src.config import settings

llm = ChatOpenAI(model = settings.CHAT_ADVANCED, temperature = 0, api_key = settings.OPENAI_API_KEY)


class TranslationRank(BaseModel):
    rank: str = Field(..., title = "Rank of the translation - 1, 2 or 3.")


template = """
You are a translator with extensive knowledge of human languages and their contextual nuances. 
You will be presented with a word in {input_language} between ### and ###.
You will be also presented a specific context in which a word was used between &&& and &&&. 
Your task is to rank a translation presented between @@@ and @@@ on a scale from 1 to 3:
- 1 indicates a contextually accurate translation,
- 2 indicates an acceptable but less precise translation
- 3 indicates an incorrect translation.

Example:
Word to translate: pies
Translation ranked 1: dog
Translation ranked 2: puppy
Translation ranked 3: cat

Example:
Word to translate: to sit
Translation ranked 1: siedzieć
Translation ranked 2: siadać
Translation ranked 3: hej

###
{word_to_translate}
###


&&&
{context}
&&&

@@@
{your_translation}
@@@

Your reply should be either a number 1, 2 or 3. Other answers will be considered invalid.
"""

prompt = PromptTemplate.from_template(template)
llm_structured = llm.with_structured_output(TranslationRank)
translate_chain = prompt | llm_structured


def get_word_translation_ranking(word_to_translate: str, proper_translation: str, context: str, input_language: str, output_language: str, your_translation: str):
    # print(f"Base form your: {base_generator(your_translation, input_language)}")
    # print(f"Base form proper: {base_generator(proper_translation, input_language)}")

    if your_translation == proper_translation:
        return {"rank": "1", "source": "proper_translation"}

    if base_generator(your_translation, input_language) == base_generator(proper_translation, input_language):
        return {"rank": "1", "source": "base_form"}

    reply = translate_chain.invoke(
        {"word_to_translate": word_to_translate,
         "proper_translation": proper_translation,
         "context": context,
         "input_language": input_language,
         "output_language": output_language,
         "your_translation": your_translation}
    )

    rank = reply.rank

    if rank in ["1", "2", "3"]:
        return {"rank": rank, "source": "AI"}
    else:
        raise ValueError("Invalid response. Please provide a number 1, 2 or 3.")

# word_to_translate = "to sit"
# proper_translation = "siedzieć"
# context = "Alice was sitting on the bank by her sister."
# input_language = "English"
# output_language = "Polish"
# your_translation = "siadać"
#
# # print(template.format(word_to_translate = word_to_translate, proper_translation = proper_translation, context = context, input_language = input_language,
# #                       output_language = output_language, your_translation = your_translation))
#
# reply = get_word_translation_ranking(word_to_translate = word_to_translate,
#                                      proper_translation = proper_translation,
#                                      context = context,
#                                      input_language = input_language,
#                                      output_language = output_language,
#                                      your_translation = your_translation)
#
# print(reply)
