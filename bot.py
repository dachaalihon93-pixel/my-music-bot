import logging
import asyncio
import os
import threading
import traceback
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

# --- BOT SOZLAMALARI ---
API_TOKEN = '8508472995:AAFSdMnR24iPZg6637DtzmZL2PPM8IFSi1U'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Diagnostika rejimi yoqildi. Muammo bo'lsa, bot xato matnini yuboradi. ✨")

# Instagram yuklovchi diagnostika bilan
@dp.message(F.text.contains("instagram.com"))
async def insta_dl(message: types.Message):
    wait = await message.answer("Instagram tahlil qilinmoqda... ⏳")
    path = f"v_{message.from_user.id}.mp4"
    opts = {
        'format': 'best', 'outtmpl': path, 'quiet': True,
        'no_check_certificate': True,
        'add_header': [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([message.text])
        await message.answer_video(video=types.FSInputFile(path))
        os.remove(path)
    except Exception as e:
        error_trace = traceback.format_exc()
        await message.answer(f"❌ **Instagram Xatosi:**\n
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2

### Bu kod nima qiladi?
1.  **`traceback` kutubxonasi:** Python-dagi xatolik aynan qaysi qatorda va nima sababdan bo'lganini to'liq ko'rsatib beradi.
2.  **To'g'ridan-to'g'ri hisobot:** Agar "Xurshid Rasulov" deb yozsangiz va qidiruvda xato bo'lsa, bot sizga "Qidiruvda xato" deyish o'rniga, texnik xatolik matnini yuboradi.
3.  **Markdown format:** Xatolik matni tushunarli bo'lishi uchun kod ko'rinishida keladi.

GitHub-da bu kodni saqlang va Render-da bot **"Live"** bo'lgach, yana bir bor qidirib ko'ring. Bot qanday xato yuborsa, o'sha matnni menga nusxalab yuboring, muammoni darhol hal qilamiz.
