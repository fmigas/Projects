from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field

from src.config import settings

llm = ChatOpenAI(model = settings.CHAT_ADVANCED, api_key = settings.OPENAI_API_KEY)


class Translation(BaseModel):
    translation: str = Field(..., title = "Translation of the sentence.")


prompt_translate_sentence = """
You are a professional translator. Translate the following sentence from {input_language} to {output_language}.
Translate the sentence using vocabulary at the level {level} of language knowledge.
Sentence:
{sentence}

"""

prompt_translate_sentence = PromptTemplate.from_template(prompt_translate_sentence)
llm_structured = llm.with_structured_output(Translation)
chain_translate_sentence = prompt_translate_sentence | llm_structured


def translate_sentence(sentence: str, level: str, input_language: str, output_language: str) -> str:
    reply = chain_translate_sentence.invoke({"sentence": sentence, "level": level, "input_language": input_language, "output_language": output_language})
    return reply.translation

