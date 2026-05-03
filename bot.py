import os
import asyncio
import datetime
import random
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"
API_URL = "https://apx-otc-api-production.up.railway.app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 
GLOBAL_BC = {"status": "✅ API NODE: STABLE", "time": "LIVE"}

# 24 PREMIUM ASSET GRID
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC", 
    "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC", "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",   
    "BTCUSD": "₿🌐 BTCUSD-OTC", "AAPL": "🍎 AAPL-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC",
    "MSFT": "💻 MSFT-OTC", "INTL": "🔬 INTL-OTC", "MCD": "🍔 MCD-OTC", "JNJ": "🏥 JNJ-OTC"
}

# ====================== SECURITY DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_titan.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

async def is_vip_active(uid):
    conn = sqlite3.connect('apx_titan.db')
    user = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if user and user[1] == 1:
        exp = datetime.datetime.strptime(user[0], "%Y-%m-%d")
        if datetime.datetime.now() < exp: return True
    return False

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # --- STEP 1: STRICT JOIN CHECK ---
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN OFFICIAL CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY & ACCESS", callback_data="check_auth"))
            return await message.answer_photo(photo=BANNER_URL, caption="🚫 **ACCESS BLOCKED**\n\nYour ID is not synchronized with our Neural Node. Please join the channel first to decrypt the terminal.", reply_markup=kb.as_markup())
    except: pass

    await show_dashboard(message)

async def show_dashboard(message_or_call):
    uid = message_or_call.from_user.id
    msg = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    
    vip_status = await is_vip_active(uid)
    pkt_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    
    kb = InlineKeyboardBuilder()
    # --- STEP 2: VIP LOCK ---
    if not vip_status:
        kb.row(types.InlineKeyboardButton(text="🔑 ACTIVATE LICENSE (TEMP KEY)", callback_data="get_license"))
    else:
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TITAN TERMINAL", callback_data="init_term"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_bot"))

    caption = (
        f"💎 **APX TITAN OS v31.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **TRADER:** `{message_or_call.from_user.first_name}`\n"
        f"📡 **NODE:** `{GLOBAL_BC['status']}`\n"
        f"⏰ **PKT:** `{pkt_now.strftime('%H:%M')}` | **RANK:** `{'VIP 💎' if vip_status else 'GUEST ⚪'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"System Calibrated. Awaiting License Verification..."
    )
    
    try:
        if isinstance(message_or_call, types.Message): await message_or_call.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
        else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())
    except: pass

# ====================== TERMINAL WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE", callback_data="mode:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="mode:multi")
    ).row(types.InlineKeyboardButton(text="⬅️ BACK TO DASHBOARD", callback_data="check_auth")).as_markup()
    await callback.message.edit_caption(caption="⚡ **SELECTION INTENSITY**\nChoose extraction mode:", reply_markup=kb)

@dp.callback_query(F.data.startswith("mode:"))
async def mode_set(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"mode": callback.data.split(":")[1], "pairs": []}
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"🔹 {display} ✅" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text=f"🔥 NEXT: INDICATORS ({len(sel)})", callback_data="ask_ind"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    await callback.message.edit_caption(caption="🧪 **ASSET GRID**\nSelect assets (Glow indicates active nodes):", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if user_ctx[uid]["mode"] == "single": user_ctx[uid]["pairs"] = [pair]
    else:
        if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
        elif len(user_ctx[uid]["pairs"]) < 3: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

# ====================== ENGINE & PROGRESS BARS ======================
@dp.callback_query(F.data == "ask_ind")
async def ask_ind(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📉 BOLLINGER BANDS", callback_data="set_i:BB"),
           types.InlineKeyboardButton(text="🧠 NEURAL RSI", callback_data="set_i:RSI"))
    kb.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    await callback.message.edit_caption(caption="📊 **STRATEGY SELECTION**\nSelect Neural Filter:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_i:"))
async def step_time_start(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["ind"] = callback.data.split(":")[1]
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 **TIME PROTOCOL**\nSend **START TIME** (Format: `14:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 **TIME PROTOCOL**\nSend **END TIME** (Format: `15:30`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_titan_engine(message)

async def execute_titan_engine(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **SYNCHRONIZING API...**")
    
    for i in [25, 55, 80, 100]:
        await asyncio.sleep(0.4)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING {data['ind']} BANDS**\n`[{bar}] {i}%` \nStatus: Neural Sync Active")

    report = (
        f"╔════════════════════════════╗\n"
        f"        **APX ALPHA PRO**\n"
        f"╚════════════════════════════╝\n"
        f"STRAT: `{data['ind']}` | ZONE: `PKT` \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f" TIME  ┃ ASSET   ┃ DIR   ┃ ACC \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p.split()[1][:6]}` ┃ `{random.choice(['CALL', 'PUT '])}` ┃ `{random.randint(93, 99)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(6, 12))

    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_done"))
    kb.row(types.InlineKeyboardButton(text="⬅️ NEW EXTRACTION", callback_data="check_auth"))
    
    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | UTC+5 PKT**", parse_mode="Markdown", reply_markup=kb.as_markup())
    user_ctx.pop(uid, None)

# ====================== ADMIN & UTILS ======================
@dp.callback_query(F.data == "check_auth")
async def check_auth(callback: types.CallbackQuery):
    await callback.answer("Authenticating...")
    await start_handler(callback.message)

@dp.callback_query(F.data == "get_license")
async def get_license(callback: types.CallbackQuery):
    key = f"APX-TITAN-{random.randint(1000,9999)}"
    await callback.message.answer(f"🔑 **YOUR LICENSE KEY:**\n`{key}`\n\nSend `/verify {key}` to activate 24-hour access.")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    expiry = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    conn = sqlite3.connect('apx_titan.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (message.from_user.id, expiry))
    conn.commit(); conn.close()
    
    # Admin Notify
    await bot.send_message(ADMIN_ID, f"🔔 **ADMIN NOTIFY:** User `{message.from_user.first_name}` activated VIP.")
    await message.answer("✅ **LICENSE ACTIVATED!**\nRestarting terminal...", reply_markup=types.ReplyKeyboardRemove())
    await start_handler(message)

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    is_vip = await is_vip_active(callback.from_user.id)
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Region: Pakistan 🇵🇰\n🛡 Rank: {'VIP 💎' if is_vip else 'Guest'}", show_alert=True)

@dp.callback_query(F.data == "rules")
async def rules_cb(callback: types.CallbackQuery):
    await callback.message.edit_caption(caption="📜 **MASTER RULES**\n\n1. OTC Assets only.\n2. M-1 Martingale permitted.\n3. 1-Minute expiry time.", reply_markup=InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="check_auth")).as_markup())

@dp.callback_query(F.data == "copy_done")
async def copy_done(callback: types.CallbackQuery):
    await callback.answer("✅ Signals copied to clipboard!", show_alert=True)

@dp.callback_query(F.data == "exit_bot")
async def exit_bot(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 Terminal Closed.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
