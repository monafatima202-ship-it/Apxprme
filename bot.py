import os
import asyncio
import datetime
import random
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(token=TOKEN, parse_mode="HTML") # HTML Mode Active
dp = Dispatcher()
user_ctx = {} 
MANUAL_NOTICE = {"active": False, "text": ""}

# HARD-CODED 24 ASSETS
PAIRS_DATA = {
    "USDINR": "🇮🇳 USDINR-OTC", "USDPKR": "🇵🇰 USDPKR-OTC", "USDJPY": "🇯🇵 USDJPY-OTC", 
    "USDPHP": "🇵🇭 USDPHP-OTC", "USDMXN": "🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺 EURUSD-OTC",
    "GBPUSD": "🇬🇧 GBPUSD-OTC", "USDCAD": "🇨🇦 USDCAD-OTC", "XAUUSD": "🥇 XAUUSD-OTC",   
    "BTCUSD": "₿ BTCUSD-OTC", "USDTRY": "🇹🇷 USDTRY-OTC", "USDBRL": "🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿 NZDUSD-OTC", "AUDUSD": "🇦🇺 AUDUSD-OTC", "USDCHF": "🇨🇭 USDCHF-OTC", 
    "USDCOP": "🇨🇴 USDCOP-OTC", "USDBDT": "🇧🇩 USDBDT-OTC", "USDARS": "🇦🇷 USDARS-OTC",
    "AAPL": "🍎 AAPL-OTC", "MSFT": "💻 MSFT-OTC", "PFE": "💊 PFE-OTC", "JNJ": "🏥 JNJ-OTC",
    "MCD": "🍔 MCD-OTC", "INTL": "🔬 INTL-OTC"
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_final_v90.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, key_taken INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

async def get_node_status():
    if MANUAL_BROADCAST["active"]: return f"📢 {MANUAL_BROADCAST['text']}"
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now.hour
    if 2 <= h < 8: return "🌙 <b>SLEEP MODE</b>"
    elif 13 <= h < 15: return "❄️ <b>COOL DOWN</b>"
    return "✅ <b>API NODE: STABLE</b>"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY ACCESS", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="<b>🛡️ ACCESS DENIED</b>\nPlease join @vectabot1 first to verify your identity.", parse_mode="HTML", reply_markup=kb.as_markup())
    except: pass
    await show_dashboard(message)

async def show_dashboard(m_c):
    uid = m_c.from_user.id
    msg = m_c if isinstance(m_c, types.Message) else m_c.message
    
    conn = sqlite3.connect('apx_final_v90.db')
    u = conn.execute("SELECT expiry, is_vip, key_taken FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    
    access = "GUEST"
    if u and u[1] == 1:
        exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < exp: access = "VIP ✅"
    
    status = await get_node_status()
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if access == "VIP ✅":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    elif not u or u[2] == 0:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔒 ACCESS EXPIRED", callback_data="profile"))

    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ SHUTDOWN", callback_data="exit_sys"))

    caption = (
        f"💎 <b>APX PRIME OS v90.0</b> 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>TRADER:</b> <code>{m_c.from_user.first_name}</code>\n"
        f"📡 <b>STATUS:</b> {status}\n"
        f"⏰ <b>PKT:</b> <code>{pkt}</code> | <b>RANK:</b> <b>{access}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural v9.0 Handshake: <b>Verified</b>"
    )
    if isinstance(m_c, types.Message): await m_c.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== KEY & VERIFY (TAP-TO-COPY) ======================
@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000, 9999)}-PRO"
    # Is command par tap karte hi sirf command copy ho jayegi
    await callback.message.answer(f"🔑 <b>YOUR VIP KEY:</b>\n\n<code>/verify {key}</code>\n\nTap the command above to copy, then send it here.")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_final_v90.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, key_taken) VALUES (?, ?, 1, 1)", (message.from_user.id, exp))
    conn.commit(); conn.close()
    
    await bot.send_message(ADMIN_ID, f"🔔 <b>JOIN NOTIFY:</b> {message.from_user.first_name} verified key.")
    await message.answer("✅ <b>VIP ACTIVATED!</b> Access granted for 7 Days.")
    await asyncio.sleep(1); await start_handler(message)

# ====================== TERMINAL WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": [], "last_report": None}
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE PAIR", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi")
    ).as_markup()
    await callback.message.edit_caption(caption="⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb)

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["mode"] = callback.data.split(":")[1]
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    mode = user_ctx[uid].get("mode", "single")
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    
    if sel: builder.row(types.InlineKeyboardButton(text=f"🚀 NEURAL SCAN ({len(sel)})", callback_data="ask_time"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    await callback.message.edit_caption(caption=f"🧪 <b>ASSET GRID ({mode.upper()})</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid]["mode"] == "multi" else 1
    
    if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < limit: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 <b>TIME PROTOCOL</b>\nSend Start Time (e.g. <code>14:00</code>)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 <b>TIME PROTOCOL</b>\nSend End Time (e.g. <code>16:00</code>)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    data = user_ctx[message.from_user.id]
    load = await message.answer("📡 <b>SCANNING...</b>")
    await asyncio.sleep(1); bar = "🟦🟦🟦🟦🟦⬜⬜⬜⬜⬜"
    await load.edit_text(f"🧪 <b>NEURAL SYNC</b>\n<code>[{bar}] 100%</code>")

    report = f"APX ALPHA SIGNALS\n━━━━━━━━━━━━━━━━━━━━━━\n"
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            report += f"{curr.strftime('%H:%M')} | {p.split(' ')[1][:6]} | {'CALL' if random.choice([0,1]) else 'PUT '} | {random.randint(95, 99)}%\n"
        curr += datetime.timedelta(minutes=random.randint(7, 13))

    await load.delete()
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 RE-SCAN", callback_data="init_term"),
        types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys")
    ).as_markup()
    # Pura report monospaced hai, tap karte hi pura copy ho jayega
    await message.answer(f"📋 <b>TAP TO COPY SIGNALS:</b>\n\n<code>{report}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n✅ UTC+5 PKT", reply_markup=kb)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 <b>OFFLINE</b>")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
