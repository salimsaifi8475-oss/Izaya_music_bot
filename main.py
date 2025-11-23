from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream, InputAudioStream
from youtubesearchpython import VideosSearch
import yt_dlp
import os

API_ID = 123456  # Your API ID
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"
SESSION = "YOUR_SESSION_STRING"  # Pyrogram Session String

app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user = Client(
    "music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

call = PyTgCalls(user)


# ------------------- YOUTUBE SEARCH -------------------
def search_youtube(query):
    results = VideosSearch(query, limit=1).result()
    if results["result"]:
        return results["result"][0]["link"]
    return None


# ------------------- AUDIO DOWNLOAD -------------------
def download_audio(url):
    file_name = "song.mp3"
    if os.path.exists(file_name):
        os.remove(file_name)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": file_name,
        "quiet": True,
        "nocheckcertificate": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return file_name


# ------------------- START COMMAND -------------------
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("🎧 **Music Bot Online!**\nUse `/play song name` to play music in VC.")


# ------------------- PLAY COMMAND -------------------
@app.on_message(filters.command("play"))
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Use: `/play kesariya`")

    query = " ".join(message.command[1:])

    await message.reply(f"🔍 Searching: **{query}**")

    url = search_youtube(query)
    if not url:
        return await message.reply("❌ Song not found.")

    await message.reply("⬇️ Downloading audio…")

    file = download_audio(url)

    chat_id = message.chat.id

    await call.join_group_call(
        chat_id,
        InputStream(
            InputAudioStream(file)
        )
    )

    await message.reply("▶️ **Playing Now!**")


# ------------------- PAUSE -------------------
@app.on_message(filters.command("pause"))
async def pause(_, message):
    await call.pause_stream(message.chat.id)
    await message.reply("⏸️ Paused")


# ------------------- RESUME -------------------
@app.on_message(filters.command("resume"))
async def resume(_, message):
    await call.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed")


# ------------------- STOP -------------------
@app.on_message(filters.command("stop"))
async def stop(_, message):
    await call.leave_group_call(message.chat.id)
    await message.reply("⏹️ Stopped")


print("Bot Running...")
user.start()
call.start()
app.run()
