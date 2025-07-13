from database import get_professions_by_category
import random


def recommend_profession(category: str):
    """
    Возвращает список профессий (1–2 штуки) по выбранной категории.
    """
    professions = get_professions_by_category(category.lower())
    
    if not professions:
        return ["Извини, пока нет данных по этой категории."]

    # Выбираем максимум 2 профессии случайно
    selected = random.sample(professions, k=min(2, len(professions)))

    # Формируем красивые ответы
    result = []
    for title, desc in selected:
        result.append(f"🔹 *{title}*\n_{desc}_")

    return result
