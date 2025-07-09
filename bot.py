import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
import openai
import os

BOT_TOKEN = "8021267990:AAE4VmVO_gGsf2_01PD3E73FQ0qwPzRPZLw"
OPENAI_API_KEY = "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"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY

SIGNS = ["овен", "телец", "близнецы", "рак", "лев", "дева",
         "весы", "скорпион", "стрелец", "козерог", "водолей", "рыбы"]
PERIODS = {"1": "сегодня", "3": "на 3 дня", "7": "на неделю"}

def build_prompt(sign: str, period: str) -> str:
    return (
        f"Составь уникальный гороскоп для знака {sign} {period}. "
        "Кратко, вдохновляюще, без шаблонов."
    )

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🔮 Привет! Напиши знак зодиака и на сколько дней нужен прогноз (1, 3 или 7).\n"
        "Пример: <b>рак 3</b>"
    )

@dp.message(F.text)
async def handle_message(message: Message):
    parts = message.text.strip().lower().split()
    if len(parts) != 2 or parts[0] not in SIGNS or parts[1] not in PERIODS:
        await message.answer(
            "Неверный формат.\n"
            "Введите, например: <b>овен 1</b>"
        )
        return

    sign, p = parts
    await message.answer("🔄 Генерирую прогноз...")

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # или GPT‑4, если доступен
            messages=[{"role": "user", "content": build_prompt(sign, PERIODS[p])}],
            temperature=0.8,
            max_tokens=200
        )
        forecast = resp.choices[0].message.content
        await message.answer(
            f"🔮 Гороскоп {PERIODS[p]} для <b>{sign.title()}</b>:\n\n{forecast}"
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("❌ Ошибка генерации. Попробуйте позже.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

