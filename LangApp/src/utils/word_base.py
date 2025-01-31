
import spacy
nlp_en = spacy.load("en_core_web_sm")
nlp_pl = spacy.load("pl_core_news_sm")


def base_generator(word: str, lang: str) -> str:
    nlp = None
    if lang == "Polish":
        nlp = nlp_pl
    if lang == "English":
        nlp = nlp_en

    doc = nlp(word)
    base = doc[0].lemma_
    return base


