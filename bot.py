import logging
import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

# --- WEBSERVER (Render uchun) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheckHandler)
    server.serve_forever()

# --- BOT ---
API_TOKEN = '8508472995:AAFSdMnR24iPZg6637DtzmZL2PPM8IFSi1U'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Xush kelibsiz! Musiqa nomi yoki Instagram linkini yuboring. ✨")

@dp.message(F.text.contains("instagram.com"))
async def insta_dl(message: types.Message):
    wait = await message.answer("Video tahlil qilinmoqda... ⏳")
    path = f"v_{message.from_user.id}.mp4"
    opts = {
        'format': 'best',
        'outtmpl': path,
        'quiet': True,
        'no_check_certificate': True,
        'add_header': [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([message.text])
        await message.answer_video(video=types.FSInputFile(path))
        os.remove(path)
    except Exception as e:
        logging.error(e)
        await message.answer("Instagram xatosi! Profil yopiq bo'lishi mumkin. ❌")
    finally:
        await wait.delete()

@dp.message()
async def music_search(message: types.Message):
    if message.text.startswith("http"): return
    wait = await message.answer("Qidirilmoqda... 🔍")
    try:
        search = VideosSearch(message.text, limit=5)
        res = search.result().get('result', [])
        if not res:
            await message.answer("Topilmadi. ❌")
            return
        kb = []
        for i in res:
            title = i.get('title', 'Musiqa')[:35]
            kb.append([InlineKeyboardButton(text=f"🎵 {title}", callback_data=f"dl_{i['id']}")])
        await message.answer("Tanlang: 👇", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    except Exception as e:
        logging.error(e)
        await message.answer("Qidiruvda xato. 🛠")
    finally:
        await wait.delete()

@dp.callback_query(F.data.startswith("dl_"))
async def music_dl(callback: types.CallbackQuery):
    v_id = callback.data.split("_")[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    path = f"{v_id}.mp3"
    await callback.answer("Yuklanmoqda... ✨")
    opts = {'format': 'bestaudio', 'outtmpl': path, 'quiet': True}
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        await callback.message.answer_audio(audio=types.FSInputFile(path))
        os.remove(path)
    except:
        await callback.message.answer("Yuklab bo'lmadi. ❌")

async def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
