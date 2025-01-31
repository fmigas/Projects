from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from src.config import settings

llm = ChatOpenAI(model = settings.CHAT_ADVANCED, api_key = settings.OPENAI_API_KEY, temperature = 0.5)


class Sentence(BaseModel):
    sentence: str = Field(..., title = "Generated sentence.")


prompt_generate_sentence = """
For a given word in {language} generate a sentence.
Generate a sentence using vocabulary at the level {level} of language knowledge.

Word:
{word}
"""

prompt_generate_sentence = PromptTemplate.from_template(prompt_generate_sentence)

llm_structured = llm.with_structured_output(Sentence)
chain_generate_sentence = prompt_generate_sentence | llm_structured


def generate_sentence(word: str, level: str, language: str) -> str:
    reply = chain_generate_sentence.invoke({"word": word, "level": level, "language": language})
    return reply.sentence


# word = "sister"
# language = "English"
# sentence_A = generate_sentence(word, "A1", language)
# sentence_B = generate_sentence(word, "B1", language)
# sentence_C = generate_sentence(word, "C2", language)
# print(sentence_A)
# print(sentence_B)
# print(sentence_C)
