
from dotenv import load_dotenv
load_dotenv("/Users/franek/Documents/PROJEKTY/pragmile/.env")

from dataclasses import dataclass
from pathlib import Path
from langchain_openai import ChatOpenAI


@dataclass
class Config:
    root: Path = Path.home() / 'Documents' / 'PROJEKTY' / 'pragmile'
    files: Path = root / 'files'
    vectorestore: Path = files / 'vectorestore'
    chat3_5 = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    chat4 = ChatOpenAI(temperature=0, model_name="gpt-4", max_retries=5, request_timeout=20)

