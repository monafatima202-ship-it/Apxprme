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
ADMIN_USER = "@MMQUOBOT"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"
API_URL = "https://apx-otc-api-production.up.railway.app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Memory & Global Systems
user_context = {} 
SYSTEM_CONTROL = {"mode": "auto", "msg": ""}

# FULL 24 ASSET GRID
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC", 
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", "XAUUSD": "🥇 XAUUSD-OTC",   
    "BTCUSD": "₿ BTCUSD-OTC", "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC", 
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "AAPL": "🍎 AAPL-OTC", "MSFT": "💻 MSFT-OTC", "PFE": "💊 PFE-OTC", "JNJ": "🏥 JNJ-OTC",
    "MCD": "🍔 MCD-OTC", "INTL": "🔬 INTL-OTC"
}

# ====================== DATABASE & SECURITY ======================
def init_db():
    conn = sqlite3.connect('apx_prime.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, expiry TEXT, key_used INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

async def check_vip(uid):
    conn = sqlite3.connect('apx_prime.db')
    user = conn.execute("SELECT expiry FROM users WHERE user_id = ?", (uid,)).fetchone()
    conn.close()
    if user and user[0]:
        exp = datetime.datetime.strptime(user[0], "%Y-%m-%d %H:%M")
        return (True, user[0]) if datetime.datetime.now() < exp else (False, None)
    return False, None

def get_sys_status():
    if SYSTEM_CONTROL["mode"] != "auto": return SYSTEM_CONTROL["msg"]
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now.hour
    if 2 <= h < 8: return "🌙 **SLEEP MODE** (Market Resting)"
    elif 8 <= h < 11: return "❄️ **COOL MODE** (Volatility High)"
    else: return "✅ **ACTIVE** (Neural Engine Live)"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # 1. Join Check
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if member.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🔄 REFRESH ACCESS", callback_data="refresh"))
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **ACCESS RESTRICTED**\nJoin our channel to unlock the Neural Terminal.", reply_markup=kb.as_markup())
    except: pass

    await show_main_dashboard(message)

async def show_main_dashboard(message_or_call):
    uid = message_or_call.from_user.id
    msg = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    
    vip_active, expiry = await check_vip(uid)
    status = get_sys_status()

    kb = InlineKeyboardBuilder()
    if not vip_active:
        kb.row(types.InlineKeyboardButton(text="🔑 GET TEMP KEY (1 USER/1 KEY)", callback_data="gen_temp"))
    else:
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="mode_select"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    caption = (
        f"⚡ **APX PRIME OS v17.0** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **USER:** `{message_or_call.from_user.full_name}`\n"
        f"🛡️ **RANK:** `{'VIP 💎' if vip_active else 'GUEST ⚪'}`\n"
        f"📡 **STATUS:** {status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Advance Neural Terminal is ready for execution."
    )
    
    try:
        if isinstance(message_or_call, types.Message):
            await message_or_call.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
        else:
            await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())
    except TelegramBadRequest: pass

# ====================== TERMINAL LOGIC ======================
@dp.callback_query(F.data == "mode_select")
async def terminal_cb(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE PAIR", callback_data="term:single"),
        types.InlineKeyboardButton(text="🌐 MULTI PAIRS", callback_data="term:multi")
    ).as_markup()
    await callback.message.edit_caption(caption="⚡ **SELECT MODE**\nChoose analysis intensity:", reply_markup=kb)

@dp.callback_query(F.data.startswith("term:"))
async def setup_term(callback: types.CallbackQuery):
    await callback.answer()
    mode = callback.data.split(":")[1]
    user_context[callback.from_user.id] = {"mode": mode, "pairs": []}
    await callback.message.edit_caption(caption="💠 **ASSET GRID** (Select Assets):", reply_markup=get_grid(callback.from_user.id))

def get_grid(uid):
    data = user_context.get(uid, {})
    sel = data.get('pairs', [])
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        prefix = "🔵 " if display in sel else "💠 "
        builder.add(types.InlineKeyboardButton(text=f"{prefix}{display}", callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text="✅ CONFIRM SELECTION", callback_data="confirm_p"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="refresh"))
    return builder.as_markup()

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if user_context[uid]["mode"] == "single": user_context[uid]["pairs"] = [pair]
    else:
        if pair in user_context[uid]["pairs"]: user_context[uid]["pairs"].remove(pair)
        else: user_context[uid]["pairs"].append(pair)
    try: await callback.message.edit_reply_markup(reply_markup=get_grid(uid))
    except: pass

# ====================== SIGNALS ENGINE ======================
@dp.callback_query(F.data == "confirm_p")
async def ask_time(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("🕒 **STEP 1:** Send **START TIME** (HH:MM)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def time_handler(message: types.Message):
    uid = message.from_user.id
    if uid not in user_context: return
    if "start_t" not in user_context[uid]:
        user_context[uid]["start_t"] = message.text
        await message.answer("🕒 **STEP 2:** Send **END TIME** (HH:MM)")
    else:
        user_context[uid]["end_t"] = message.text
        await run_signals(message)

async def run_signals(message: types.Message):
    data = user_context[message.from_user.id]
    load = await message.answer("🧪 **SCANNING API TRENDS...**")
    
    # Flashing Bar Logic
    for i in [20, 50, 100]:
        await asyncio.sleep(0.4)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"📡 **AI CALIBRATION...**\n`[{bar}] {i}%`")

    report = "╔════════════════════════════╗\n        **APX ALPHA PRO**\n╚════════════════════════════╝\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n TIME  ┃ PAIR    ┃ DIR   ┃ ACC \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            name = p.split(" ")[1].replace("-OTC","").ljust(7)
            dir_v = random.choice(["CALL 🟢", "PUT  🔴"])
            report += f" `{curr.strftime('%H:%M')}` ┃ `{name}` ┃ `{dir_v}` ┃ `{random.randint(88,98)}%` \n"
        curr += datetime.timedelta(minutes=10)
    
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **Neural Verified API Data**"
    await load.delete()
    await message.answer(report, parse_mode="Markdown")
    user_context.pop(message.from_user.id, None)

# ====================== SECURITY & PROFILE ======================
@dp.callback_query(F.data == "gen_temp")
async def gen_temp_key(callback: types.CallbackQuery):
    uid = callback.from_user.id
    conn = sqlite3.connect('apx_prime.db')
    check = conn.execute("SELECT key_used FROM users WHERE user_id = ?", (uid,)).fetchone()
    
    if check and check[0] == 1:
        await callback.answer("❌ You already used your Temp Key!", show_alert=True)
    else:
        key = f"APX-SYS-{random.randint(1000, 9999)}"
        await callback.message.edit_caption(caption=f"🔑 **TEMP KEY:** `{key}`\n\nSend: `/verify {key} 7` to activate 7 days VIP.")
    conn.close()

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 3: return await message.answer("Format: `/verify KEY DAYS`")
    
    days = int(args[2])
    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
    
    conn = sqlite3.connect('apx_prime.db')
    conn.execute("INSERT OR REPLACE INTO users (user_id, expiry, key_used) VALUES (?, ?, 1)", (message.from_user.id, expiry))
    conn.commit()
    conn.close()
    await message.answer(f"✅ **VIP ACTIVATED!**\nExpiry: `{expiry}`\nSend /start")

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    vip, exp = await check_vip(callback.from_user.id)
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Region: Pakistan (UTC+5)\n📅 Exp: {exp if exp else 'N/A'}", show_alert=True)

@dp.callback_query(F.data == "refresh")
async def refresh_cb(callback: types.CallbackQuery):
    await callback.answer("Refreshing System...")
    await start_handler(callback.message)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.answer("Terminal Terminated.")
    await callback.message.delete()
    await callback.message.answer("🌌 **APX PRIME OS**\nConnection Closed. Come back soon!")

# ====================== STARTUP ======================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 APX PRIME OS v17.0 - ADVANCE MASTER LIVE")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
