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

# --- WEBSERVER (Render "uyg'oq" turishi uchun) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

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
    await message.answer("Assalomu alaykum! Musiqa nomi yoki Instagram linkini yuboring. ✨")

# Instagram yuklovchi
@dp.message(F.text.contains("instagram.com"))
async def insta_dl(message: types.Message):
    wait = await message.answer("Video yuklanmoqda... ⏳")
    path = f"v_{message.from_user.id}.mp4"
    opts = {
        'format': 'best', 'outtmpl': path, 'quiet': True,
        'no_check_certificate': True,
        'add_header': [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([message.text])
        await message.answer_video(video=types.FSInputFile(path), caption="Tayyor! ✅")
        os.remove(path)
    except Exception as e:
        logging.error(f"Insta Error: {e}")
        await message.answer("Instagram videoni yuklab bo'lmadi. ❌")
    finally:
        await wait.delete()

# Musiqa qidirish (Optimallashgan variant)
@dp.message()
async def music_search(message: types.Message):
    if message.text.startswith("http"): return
    wait = await message.answer("Musiqa qidirilmoqda... 🔍")
    try:
        # Qidiruvni amalga oshirish
        search = VideosSearch(message.text, limit=5)
        results = search.result()
        
        if not results or 'result' not in results or len(results['result']) == 0:
            await message.answer("Hech narsa topilmadi. ❌")
            return

        kb_list = []
        for i in results['result']:
            title = i.get('title', 'Musiqa')[:35]
            v_id = i.get('id')
            if v_id:
                kb_list.append([InlineKeyboardButton(text=f"🎵 {title}", callback_data=f"dl_{v_id}")])
        
        if not kb_list:
            await message.answer("Qidiruv natijalari yaroqsiz. ❌")
            return

        await message.answer("Variantlardan birini tanlang: 👇", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_list))
    except Exception as e:
        logging.error(f"Search Error: {e}")
        await message.answer("Qidiruvda texnik xato yuz berdi. 🛠")
    finally:
        await wait.delete()

# Musiqani yuklab berish
@dp.callback_query(F.data.startswith("dl_"))
async def music_dl(callback: types.CallbackQuery):
    v_id = callback.data.split("_")[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    path = f"{v_id}.mp3"
    await callback.answer("Musiqa tayyorlanmoqda... ✨")
    
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': path,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        await callback.message.answer_audio(audio=types.FSInputFile(path))
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logging.error(f"Download Error: {e}")
        await callback.message.answer("Musiqani yuklab bo'lmadi. ❌")

async def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
