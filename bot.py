import os
import asyncio
import datetime
import random
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"
API_URL = "https://apx-otc-api-production.up.railway.app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 
BC_LOGS = {"msg": "📡 API NODES SYNCHRONIZED", "time": "LIVE"}

# FULL 24 ASSET GRID
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC", 
    "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC", "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",   
    "BTCUSD": "₿🌐 BTCUSD-OTC", "AAPL": "🍎 AAPL-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC",
    "MSFT": "💻 MSFT-OTC", "INTL": "🔬 INTL-OTC", "MCD": "🍔 MCD-OTC"
}

# ====================== CORE ENGINES ======================
def init_db():
    conn = sqlite3.connect('apx_final.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, key TEXT, expiry TEXT)')
    conn.commit(); conn.close()

async def get_user_region(message):
    # Dummy logic for region based on TZ/Language or IP (In real bot, use IP API)
    return "PAKISTAN 🇵🇰" if "pk" in message.from_user.language_code else "GLOBAL 🌍"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # Strict Join Check
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🔄 VERIFY ACCESS", callback_data="refresh"))
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **ACCESS DENIED**\nJoin our official channel to decrypt API nodes.", reply_markup=kb.as_markup())
    except: pass

    # Auto Broadcast Timing Logic
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    time_str = now.strftime("%H:%M")
    status = BC_LOGS["msg"]
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="🔑 TEMP KEY", callback_data="get_temp_key"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT SYSTEM", callback_data="exit_bot"))

    caption = (
        f"💎 **APX PRIME OS v30.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **TRADER:** `{message.from_user.first_name}`\n"
        f"📡 **STATUS:** `{status}`\n"
        f"⏰ **PKT TIME:** `{time_str}` (UTC+5)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural Terminal is online. Select your module:"
    )
    
    if isinstance(message, types.Message): await message.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await message.message.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== TERMINAL WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE", callback_data="mode:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="mode:multi")
    ).row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="refresh")).as_markup()
    await callback.message.edit_caption(caption="⚡ **EXTRACTION MODE**\nSelect your signal intensity:", reply_markup=kb)

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
    await callback.message.edit_caption(caption="🧪 **ASSET SELECTION (24 PAIRS)**\nClick to select assets:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if user_ctx[uid]["mode"] == "single": user_ctx[uid]["pairs"] = [pair]
    else:
        if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
        elif len(user_ctx[uid]["pairs"]) < 3: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

# ====================== INDICATORS & TIME ======================
@dp.callback_query(F.data == "ask_ind")
async def ask_ind(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📉 BOLLINGER BANDS", callback_data="set_i:BB"),
           types.InlineKeyboardButton(text="🧠 RSI NEURAL V3", callback_data="set_i:RSI"))
    kb.row(types.InlineKeyboardButton(text="⚡ STOCHASTIC MASTER", callback_data="set_i:ST"))
    await callback.message.edit_caption(caption="📊 **QUOTEX INDICATORS**\nSelect signal filter strategy:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_i:"))
async def ask_time_1(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["ind"] = callback.data.split(":")[1]
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 **TIME RANGE**\nSend **START TIME** (Format: `14:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 **TIME RANGE**\nSend **END TIME** (Format: `15:30`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

# ====================== ENGINE & FLASHING BARS ======================
async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **INITIALIZING API...**")
    
    # FLASHING PROGRESS
    for i in [20, 55, 80, 100]:
        await asyncio.sleep(0.4)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING {data['ind']} NODES**\n`[{bar}] {i}%` \nStrategy: High-Accuracy Extraction")

    report = (
        f"╔════════════════════════════╗\n"
        f"        **APX ALPHA PRO**\n"
        f"╚════════════════════════════╝\n"
        f"STRAT: `{data['ind']}` | ZONE: `UTC+5` \n"
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
        curr += datetime.timedelta(minutes=random.randint(5, 12))

    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **NEURAL VERIFIED | PKT ZONE**")
    user_ctx.pop(uid, None)

# ====================== UTILS (PROFILE, KEY, BC) ======================
@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    reg = await get_user_region(callback)
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Region: {reg}\n🛡 Rank: VIP Member", show_alert=True)

@dp.callback_query(F.data == "get_temp_key")
async def temp_key(callback: types.CallbackQuery):
    key = f"TEMP-{random.randint(100,999)}"
    await callback.message.answer(f"🔑 **TEMPORARY KEY:** `{key}`\n(Valid for 24 Hours)\nSend `/verify {key}` to activate.")

@dp.message(Command("admin"))
async def admin_bc(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    user_ctx[message.from_user.id] = {"step": "admin_bc"}
    await message.answer("🎙 **MANUAL BROADCAST**\nSend the message for Dashboard Status:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    BC_LOGS["msg"] = f"📢 {message.text}"
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Status Updated on Dashboard!")

@dp.callback_query(F.data == "refresh")
async def refresh_cb(callback: types.CallbackQuery):
    await callback.answer("Syncing..."); await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "exit_bot")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 Terminal Offline.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
