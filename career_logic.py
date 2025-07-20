import random
from database import get_professions_by_category


def recommend_profession(category: str, top_n: int = 5):
    """
    Возвращает топ профессий (по умолчанию 5) по выбранной категории.
    """
    professions = get_professions_by_category(category.lower())

    if not professions:
        return ["Извини, пока нет данных по этой категории."]

    random.shuffle(professions)  # случайный порядок
    selected = professions[:top_n]

    result = []
    for title, desc in selected:
        result.append(f"🔹 *{title}*\n_{desc}_")

    return result




