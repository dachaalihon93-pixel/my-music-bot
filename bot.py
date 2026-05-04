import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

# KOYEB-DA PROXY SHART EMAS
API_TOKEN = '8508472995:AAFSdMnR24iPZg6637DtzmZL2PPM8IFSi1U' 
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Koyeb orqali 24/7 ishlaydigan botga xush kelibsiz! 🔥\nLink yuboring yoki musiqa nomini yozing.")

@dp.message(F.text.contains("instagram.com"))
async def insta_dl(message: types.Message):
    wait = await message.answer("Video yuklanmoqda... ⏳")
    path = f"v_{message.from_user.id}.mp4"
    opts = {
        'format': 'best', 'outtmpl': path, 'quiet': True,
        'add_header': [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([message.text])
        await message.answer_video(video=types.FSInputFile(path))
        os.remove(path)
    except:
        await message.answer("Xatolik! Linkni tekshiring. ❌")
    finally:
        await wait.delete()

@dp.message()
async def music_search(message: types.Message):
    if message.text.startswith("http"): return
    search = VideosSearch(message.text, limit=5)
    res = search.result()['result']
    if not res:
        await message.answer("Topilmadi. ❌")
        return
    kb = []
    for i in res:
        kb.append([InlineKeyboardButton(text=i['title'][:35], callback_data=f"dl_{i['id']}")])
    await message.answer("Tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("dl_"))
async def music_dl(callback: types.CallbackQuery):
    v_id = callback.data.split("_")[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    path = f"{v_id}.mp3"
    opts = {'format': 'bestaudio', 'outtmpl': path, 'quiet': True}
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        await callback.message.answer_audio(audio=types.FSInputFile(path))
        os.remove(path)
    except:
        await callback.message.answer("Xato! ❌")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
