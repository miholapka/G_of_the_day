import asyncio
import json
from datetime import datetime
from pathlib import Path
from random import choice

from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatType
from aiogram.utils import executor

import os
API_TOKEN = os.getenv("API_TOKEN")  # <-- ВСТАВЬ СЮДА СВОЙ ТОКЕН
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DATA_FILE = Path("pidor_data.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@dp.message_handler(commands=['pidor'])
async def handle_pidor_command(message: types.Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("Эта команда работает только в группах!")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    chat_id = str(message.chat.id)
    data = load_data()

    if chat_id in data and data[chat_id]["date"] == today:
        user = data[chat_id]["user"]
        await message.reply(f"Сегодняшний пидор дня уже выбран: {user} 🏳️‍🌈")
        return

    admins = await bot.get_chat_administrators(message.chat.id)
    admin_ids = [admin.user.id for admin in admins]
    
    members = []
    async for user in bot.iter_chat_members(message.chat.id):
        if user.user.id not in admin_ids and not user.user.is_bot:
            members.append(user.user)

    if not members:
        await message.reply("Не удалось найти подходящих участников.")
        return

    chosen = choice(members)
    name = chosen.full_name

    data[chat_id] = {
        "date": today,
        "user": name
    }
    save_data(data)

    await message.reply(f"🌈 Сегодняшний пидор дня: {name}!")

if __name__ == '__main__':
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
