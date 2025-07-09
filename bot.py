
import logging
import openai
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения оставшихся бесплатных прогнозов
free_uses = {}

SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
    "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
]

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for sign in SIGNS:
        keyboard.add(types.KeyboardButton(sign))
    await message.answer("Привет! Выбери свой знак зодиака:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in SIGNS)
async def sign_selected(message: types.Message):
    user_id = message.from_user.id
    sign = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("1 день", "3 дня", "7 дней")
    keyboard.add("🔙 Назад")
    await message.answer(f"Ты выбрал {sign}. На какой срок нужен гороскоп?", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["1 день", "3 дня", "7 дней"])
async def forecast_handler(message: types.Message):
    user_id = message.from_user.id
    period = message.text
    sign = "неизвестный знак"
    async for m in bot.iter_history(message.chat.id, limit=5):
        if m.text in SIGNS:
            sign = m.text
            break

    if user_id not in free_uses:
        free_uses[user_id] = 3

    if free_uses[user_id] > 0:
        free_uses[user_id] -= 1
        prompt = f"Сделай уникальный гороскоп для знака {sign} на {period}. Без повторов, стиль дружелюбный."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        forecast = response.choices[0].message.content
       await message.answer(f"🔮 Гороскоп на {period} для {sign}:\n\n{forecast}")

        await message.answer(f"Осталось бесплатных прогнозов: {free_uses[user_id]}")
    else:
        await message.answer("❗ Вы использовали 3 бесплатных прогноза.

💎 Для доступа к неограниченным прогнозам напишите админу: @ваш_ник_или_ссылка")

@dp.message_handler(lambda message: message.text == "🔙 Назад")
async def back_handler(message: types.Message):
    await start_handler(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
