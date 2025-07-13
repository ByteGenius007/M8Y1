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

# --- FSM состояние ---
class Quiz(StatesGroup):
    answering = State()

# --- Кнопки ---
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

# --- Инициализация ---
bot = Bot(token=TOKEN)
dp = Dispatcher()
init_db()

# --- Команда старт ---
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я помогу тебе выбрать подходящую профессию.\nОтвечай на вопросы, выбирая 'Да' или 'Нет'."
    )
    await state.set_state(Quiz.answering)
    await state.update_data(current_q=0, scores={})
    await message.answer(questions[0]["text"], reply_markup=yes_no_kb)

# --- Обработка ответов ---
@dp.message(Quiz.answering, F.text.lower().in_(["да", "нет"]))
async def handle_quiz(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data["current_q"]
    scores = data["scores"]
    answer_text = message.text.lower()

    current_question = questions[q_index]

    # Получаем нужный ключ (yes или no)
    if answer_text == "да":
        direction = current_question.get("yes")
    else:
        direction = current_question.get("no")

    # Добавляем балл, если направление есть
    if direction:
        scores[direction] = scores.get(direction, 0) + 1

    # Переход к следующему вопросу
    q_index += 1
    if q_index < len(questions):
        await state.update_data(current_q=q_index, scores=scores)
        await message.answer(questions[q_index]["text"], reply_markup=yes_no_kb)
    else:
        await state.clear()

        if not scores:
            await message.answer("Ты дал нейтральные ответы 🤷‍♂️ Попробуй пройти тест снова /start")
            return

        best = max(scores, key=scores.get)
        await message.answer(f"По твоим ответам тебе подойдёт направление: *{best.capitalize()}*", parse_mode="Markdown")
        save_user(message.from_user.id, best)

        results = recommend_profession(best)
        for res in results:
            await message.answer(res, parse_mode="Markdown")

        await message.answer("Хочешь пройти тест ещё раз? Напиши /start")


# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


