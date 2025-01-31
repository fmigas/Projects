from src.llm.rank_translation import get_word_translation_ranking
from src.utils.mongo_functions import update_word_in_mongo
from src.utils.next_repetition import get_next_repetition_date


# ! dodać kontekst - cały tekst

def update_and_rank_word(word_: dict, translation_: str, context: str = " ", calculate_next_repetition: bool = False) -> tuple[int, str]:
    rank = get_word_translation_ranking(word_to_translate = word_['word'],
                                        proper_translation = word_['translation'],
                                        context = context,
                                        input_language = word_['native_language'],
                                        output_language = word_['learned_language'],
                                        your_translation = translation_, )

    # print(f"Ranking: {rank} for word {word_['word']} and translation {translation_}")
    rank = int(rank['rank'])

    word_retrained = word_.get('word_retrained', False)
    if not word_retrained and calculate_next_repetition:
        next_repetition = get_next_repetition_date(word = word_, current_rank = rank)
    else:
        next_repetition = None

    update_word_in_mongo(word_id = word_['word_id'], update_ranking = rank, first_seen_false = True, repetition_date = next_repetition)
    return rank, word_['translation']
