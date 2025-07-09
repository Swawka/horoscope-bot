import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Новый способ инициализации бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

client = OpenAI(api_key=OPENAI_API_KEY)

signs = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
    "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
]

periods = {
    "Сегодня": "today",
    "3 дня": "3days",
    "Неделя": "week"
}


def get_sign_buttons():
    builder = InlineKeyboardBuilder()
    for sign in signs:
        builder.button(text=sign, callback_data=f"sign:{sign}")
    builder.adjust(3)
    return builder.as_markup()


def get_period_buttons(sign: str):
    builder = InlineKeyboardBuilder()
    for title, key in periods.items():
        builder.button(text=title, callback_data=f"period:{key}:{sign}")
    builder.adjust(3)
    return builder.as_markup()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🔮 Добро пожаловать в AI-гороскоп бот!\nВыберите ваш знак зодиака:",
        reply_markup=get_sign_buttons()
    )


@dp.callback_query(F.data.startswith("sign:"))
async def choose_sign(callback):
    sign = callback.data.split(":")[1]
    await callback.message.edit_text(
        f"🕒 Вы выбрали <b>{sign}</b>. На какой период хотите гороскоп?",
        reply_markup=get_period_buttons(sign)
    )


@dp.callback_query(F.data.startswith("period:"))
async def send_horoscope(callback):
    _, period, sign = callback.data.split(":")
    prompt = (
        f"Составь уникальный гороскоп на {period} для знака зодиака {sign}. "
        f"Он должен быть интересным, вдохновляющим и не повторяться, без шаблонов."
    )

    await callback.message.edit_text("🔮 Генерирую гороскоп...")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        forecast = response.choices[0].message.content
    except Exception as e:
        forecast = f"Произошла ошибка при генерации гороскопа 😢\n\n{str(e)}"

    await callback.message.answer(f"🔮 Гороскоп на {period} для {sign}:\n\n{forecast}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
