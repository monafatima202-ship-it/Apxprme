import os
import asyncio
import datetime
import random
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# ====================== CONFIG ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873
CHANNEL_USERNAME = "@vectabot1"  # Change if needed
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {}
GLOBAL_BC = {"mode": "auto", "text": ""}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_prime_master.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

async def check_access(uid):
    conn = sqlite3.connect('apx_prime_master.db')
    u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if u and u[1] == 1:
        try:
            expiry_dt = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
            if datetime.datetime.now() < expiry_dt:
                return "ACTIVE"
        except:
            pass
    return "LOCKED"

# ====================== START & DASHBOARD ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id

    # Strict Channel Join Check
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if member.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder()
            kb.row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
            kb.row(types.InlineKeyboardButton(text="✅ CHECK ACCESS", callback_data="check_join"))
            return await message.answer_photo(
                photo=BANNER_URL,
                caption="🛡️ **STRICT AUTHENTICATION REQUIRED**\n\nJoin our official channel to unlock APX Prime Terminal.",
                reply_markup=kb.as_markup()
            )
    except:
        pass

    await show_main_dashboard(message)

async def show_main_dashboard(obj):
    uid = obj.from_user.id
    is_message = isinstance(obj, types.Message)
    msg = obj if is_message else obj.message

    access = await check_access(uid)
    pkt_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")

    kb = InlineKeyboardBuilder()
    if access == "ACTIVE":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 24H TEMP ACCESS", callback_data="gen_key"))

    kb.row(
        types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"),
        types.InlineKeyboardButton(text="📜 RULES", callback_data="rules")
    )
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit"))

    caption = f"""
🌌 **APX PRIME OS v5.1** 🌌
━━━━━━━━━━━━━━━━━━━━━━
👤 **User:** `{obj.from_user.first_name}`
📡 **Node:** ✅ **STABLE**
🕰️ **PKT:** `{pkt_time}` | **RANK:** `{'VIP 💎' if access == 'ACTIVE' else 'GUEST 🔒'}`
━━━━━━━━━━━━━━━━━━━━━━
**Institutional Handshake:** `Verified` 🟢
"""

    if is_message:
        await obj.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else:
        try:
            await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())
        except:
            await msg.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())

# ====================== KEY GENERATION & VERIFY ======================
@dp.callback_query(F.data == "gen_key")
async def gen_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000,9999)}-VIP"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📋 COPY KEY", callback_data=f"copykey:{key}"))
    
    await callback.message.answer(
        f"🔑 **YOUR LICENSE KEY**\n\n"
        f"`/verify {key}`\n\n"
        f"Tap button below to copy easily.",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("copykey:"))
async def copy_key(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    await callback.answer(f"Copied: {key}", show_alert=True)

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    uid = message.from_user.id
    exp = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('apx_prime_master.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (uid, exp))
    conn.commit()
    conn.close()

    # Better Celebration
    await message.answer("🎇")
    await asyncio.sleep(0.6)
    await message.answer("🎆")
    await asyncio.sleep(0.6)
    await message.answer_photo(
        photo="https://i.imgur.com/4z4fK3L.gif",  # Fireworks GIF (you can change)
        caption="🥳 **NEURAL ACCESS GRANTED!**\n\nTerminal Unlocked Successfully!\nLoading Dashboard..."
    )
    await asyncio.sleep(2)
    await start_handler(message)  # Refresh dashboard

# ====================== TERMINAL (Already Good - Minor Fixes) ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": []}
    await render_grid(callback)

# ... (baaki terminal code same rakh sakte ho ya mujhe bolo agar isme bhi changes chahiye)

@dp.callback_query(F.data == "check_join")
async def check_join(callback: types.CallbackQuery):
    await callback.message.delete()
    await start_handler(callback.message)

@dp.callback_query(F.data == "profile")
async def profile(callback: types.CallbackQuery):
    await callback.answer(f"👤 {callback.from_user.first_name}\n🌍 Pakistan (PKT)", show_alert=True)

@dp.callback_query(F.data == "exit")
async def exit_sys(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("🌌 **APX PRIME TERMINAL OFFLINE**")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
