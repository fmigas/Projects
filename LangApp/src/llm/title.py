from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field

from src.config import settings

llm = ChatOpenAI(model = settings.CHAT_ADVANCED, api_key = settings.OPENAI_API_KEY)


class Title(BaseModel):
    title: str = Field(..., title = "Title of the body.")


prompt = """
For a given body of text generate a consise, short title.

Body:
{body}
"""

# body = "Wlazł kotek na płotek i rozlał mleczko i to koniec bajeczki."

prompt = PromptTemplate.from_template(prompt)

llm_structured = llm.with_structured_output(Title)

chain = prompt | llm_structured


def generate_title(body: str) -> str:
    reply = chain.invoke({"body": body})
    return reply.title


# body = "Alice was beginning to get very tired of sitting by her sister on the bank and having nothing to do."
# title = generate_title(body)
# print(title)
