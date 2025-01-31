from datetime import datetime, timedelta

from dateutil.utils import today
from loguru import logger

'''
USTALENIE DATY KOLEJNEJ POWTÓRKI DLA SŁÓWKA
1. używając word[_id'] wgrywamy word.ranking z bazy
2. wyświetlamy słówko do powtórki i ustalamy ocenę
3. funkcja calculate_next_repetition oblicza datę kolejnej powtórki na podstawie historii ocen i nowej oceny
4. zapisujemy nową parę datę-ocena do bazy:
 - użyć funkcji jak update_word_in_mongo z mongo_functions.py, która ustala next_repetition oraz dodaje wartość do listy word.ranking 


'''


def get_next_repetition_date(word: dict, current_rank: int):
    ranking = word['ranking']
    grades = [r['score'] for r in ranking]
    # logger.info(f"Last repetition for word {word['word']} was on {ranking[-1]['date'].strftime('%Y-%m-%d')} with grade {grades[-1]}")

    if len(ranking) > 1:
        last_interval = ranking[-1]['date'] - ranking[-2]['date']
        last_interval = last_interval.days
        last_interval = max(last_interval, 1)
    else:
        last_interval = 1

    if current_rank > 1:
        new_interval = 1
    else:
        ease_factor = 2.5

        for grade in grades[-3:]:
            grade = int(grade)
            if grade == 1:  # Best grade
                ease_factor += 0.2
            elif grade == 2:  # Medium grade
                ease_factor -= 0.4
            elif grade == 3:  # Lowest grade
                ease_factor -= 1.0

        ease_factor = max(ease_factor, 0.5)
        new_interval = int(round(last_interval * ease_factor))
        new_interval = min(new_interval, 150)

    new_interval = max(new_interval, 1)
    new_date = today() + timedelta(days = new_interval)
    logger.info(f"New interval for word {word['word']} is {new_interval} days which makes date {new_date.strftime('%Y-%m-%d')}")
    return new_date
