import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
from test_questions import questions
from career_logic import recommend_profession
from database import init_db, save_user
from config import ADMIN_ID

# --- FSM состояние ---
class Quiz(StatesGroup):
    answering = State()

ADMIN_ID = ADMIN_ID

# --- Кнопки ---
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

class AddProfession(StatesGroup):
    title = State()
    category = State()
    description = State()


bot = Bot(token=TOKEN)
dp = Dispatcher()
init_db()

# --- Команда старт ---
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 *Привет!*\n\n"
        "Я — бот, который поможет тебе выбрать профессию по интересам. 🧭\n"
        "Отвечай на простые вопросы *Да* или *Нет*, а в конце я предложу тебе подходящее направление и список профессий.\n\n"
        "🧠 Готов? Тогда начнём!"
    )
    await message.answer(text, reply_markup=yes_no_kb, parse_mode="Markdown")
    await state.set_state(Quiz.answering)
    await state.update_data(current_q=0, scores={})
    await message.answer(questions[0][0], reply_markup=yes_no_kb)


# --- Обработка ответов ---
@dp.message(Quiz.answering, F.text.lower().in_(["да", "нет"]))
async def handle_quiz(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data["current_q"]
    scores = data["scores"]
    answer_text = message.text.lower()

    current_question = questions[q_index]
    question_text, direction, weight = current_question

    if answer_text == "да" and direction:
        scores[direction] = scores.get(direction, 0) + weight  # Учитываем вес

    # Переход к следующему вопросу
    q_index += 1
    if q_index < len(questions):
        await state.update_data(current_q=q_index, scores=scores)
        await message.answer(questions[q_index][0], reply_markup=yes_no_kb)
    else:
        await state.clear()

        if not scores:
            await message.answer("Ты дал нейтральные ответы 🤷‍♂️ Попробуй пройти тест снова /retry")
            return

        best = max(scores, key=scores.get)
        await message.answer(f"По твоим ответам тебе подойдёт направление: *{best.capitalize()}*", parse_mode="Markdown")
        save_user(message.from_user.id, best)

        results = recommend_profession(best)
        for res in results:
            await message.answer(res, parse_mode="Markdown")

        await message.answer("Хочешь пройти тест ещё раз? Напиши /retry")


@dp.message(Command("add_profession"))
async def cmd_add_profession(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Ты не админ.")
        return
    await message.answer("Введите название новой профессии:")
    await state.set_state(AddProfession.title)


@dp.message(AddProfession.title)
async def set_prof_name(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("""Укажите направление (технологии, люди, творчество, экономика, медицина,
        военное дело, производство, образование, наука,
        искусство, спорт, экология, инженерия, логистика):""")
    await state.set_state(AddProfession.category)


@dp.message(AddProfession.category)
async def set_prof_category(message: Message, state: FSMContext):
    category = message.text.lower()
    allowed_categories = [
        "технологии", "люди", "творчество", "экономика", "медицина",
        "военное дело", "производство", "образование", "наука",
        "искусство", "спорт", "экология", "инженерия", "логистика"
    ]
    if category not in allowed_categories:
        await message.answer("⚠ Направление должно быть одним из: " + ", ".join(allowed_categories))
        return

    await state.update_data(category=category)
    await message.answer("Введите краткое описание профессии:")
    await state.set_state(AddProfession.description)


@dp.message(AddProfession.description)
async def save_profession(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    category = data["category"]
    description = message.text

    print("Добавляем профессию:")
    print(f"Название: {title}")
    print(f"Категория: {category}")
    print(f"Описание: {description}")


    from database import add_profession
    add_profession(category, title, description)

    await message.answer("✅ Профессия успешно добавлена!")
    await state.clear()


@dp.message(Command("help"))
async def help_command(message: Message):
    text = (
        "🧭 *Доступные команды:*\n\n"
        "/start — начать тест заново\n"
        "/help — показать эту справку\n"
        "/add\\_profession — добавить профессию \\(для админа\\)\n"
        "/retry — пройти тест ещё раз"
    )
    await message.answer(text, parse_mode="MarkdownV2")



@dp.message(Command("retry"))
async def retry_test(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Quiz.answering)
    await state.update_data(current_q=0, scores={})
    await message.answer("Начнём заново! Ответь 'Да' или 'Нет' 👇")
    await message.answer(questions[0][0], reply_markup=yes_no_kb)


# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


