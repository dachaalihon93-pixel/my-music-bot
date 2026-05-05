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

# --- HEALTH CHECK SERVER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Alive")

def run_web_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheckHandler)
    server.serve_forever()

# --- BOT SETUP ---
API_TOKEN = '8508472995:AAFSdMnR24iPZg6637DtzmZL2PPM8IFSi1U'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Diagnostika tizimi ishga tushdi. Muammo bo'lsa, xato matni keladi.")

# Instagram yuklash qismi
@dp.message(F.text.contains("instagram.com"))
async def insta_dl(message: types.Message):
    wait = await message.answer("Instagram tekshirilmoqda...")
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
        if os.path.exists(path): os.remove(path)
    except Exception:
        err = traceback.format_exc()
        await message.answer(f"INSTA ERROR:\n{err[:3500]}")
    finally:
        await wait.delete()

# Musiqa qidirish qismi
@dp.message()
async def music_search(message: types.Message):
    if message.text.startswith("http"): return
    wait = await message.answer(f"Qidirilmoqda: {message.text}")
    try:
        # Bu qator ko'pincha Render-da xato beradi
        search = VideosSearch(message.text, limit=5)
        res = search.result()
        
        if not res or not res.get('result'):
            await message.answer("Natija topilmadi.")
            return

        kb = []
        for i in res['result']:
            t = i.get('title', 'Musiqa')[:35]
            vid = i.get('id')
            if vid:
                kb.append([InlineKeyboardButton(text=f"🎵 {t}", callback_data=f"dl_{vid}")])
        
        await message.answer("Tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
            
    except Exception:
        err = traceback.format_exc()
        await message.answer(f"SEARCH ERROR:\n{err[:3500]}")
    finally:
        await wait.delete()

# Musiqa yuklash qismi
@dp.callback_query(F.data.startswith("dl_"))
async def music_dl(callback: types.CallbackQuery):
    v_id = callback.data.split("_")[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    path = f"{v_id}.mp3"
    await callback.answer("Yuklash boshlandi...")
    
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': path,
        'quiet': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        await callback.message.answer_audio(audio=types.FSInputFile(path))
        if os.path.exists(path): os.remove(path)
    except Exception:
        err = traceback.format_exc()
        await callback.message.answer(f"DOWNLOAD ERROR:\n{err[:3500]}")

async def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
