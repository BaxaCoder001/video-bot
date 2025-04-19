# bot.py


import json
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMember
from config import BOT_TOKEN, OBUNA_KANALI, REKLAMA_MATNI
import subprocess

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

USERS_FILE = "user_ids.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

user_download_count = {}

# Obuna tekshiruvi
async def tekshir_obuna(user_id):
    try:
        member = await bot.get_chat_member(OBUNA_KANALI, user_id)
        return member.status in ['member', 'administrator', 'owner']
    except Exception as e:
        print(f"Obuna tekshiruvda xatolik: {e}")
        return False

# Video yuklab yuborish
async def yukla_va_joonat(link, message):
    file_name = f"{message.from_user.id}.mp4"
    cmd = ["yt-dlp", "-o", file_name, link]
    subprocess.run(cmd)
    if os.path.exists(file_name):
        await message.answer_video(video=open(file_name, "rb"))
        os.remove(file_name)
    else:
        await message.reply("Video yuklab bo‘lmadi. Linkni tekshiring.")

# Xabarni qayta ishlash
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)
    obuna = await tekshir_obuna(user_id)
    if not obuna:
        await message.reply(f"Avval {OBUNA_KANALI} ga obuna bo‘ling, keyin qaytadan urinib ko‘ring.")
        return

    with open(USERS_FILE, "r") as f:
        ids = json.load(f)
    if user_id not in ids:
        ids.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(ids, f)

    count = user_download_count.get(user_id, 0) + 1
    user_download_count[user_id] = count

    await yukla_va_joonat(message.text, message)

    if count % 3 == 0:
        await message.answer(REKLAMA_MATNI)

# Botni ishga tushurish
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
