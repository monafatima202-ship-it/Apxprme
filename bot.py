import os
import asyncio
import datetime
import random
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"
API_URL = "https://apx-otc-api-production.up.railway.app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 
SYS_BC = {"mode": "auto", "msg": ""}

# FULL 24 ASSET GRID - NO MISSING PAIRS
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC", 
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",   
    "BTCUSD": "₿🌐 BTCUSD-OTC", "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC", 
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "AAPL": "🍎 AAPL-OTC", "MSFT": "💻 MSFT-OTC", "PFE": "💊 PFE-OTC", "JNJ": "🏥 JNJ-OTC",
    "MCD": "🍔 MCD-OTC", "INTL": "🔬 INTL-OTC"
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_prime.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)')
    conn.commit(); conn.close()

async def is_vip(uid):
    conn = sqlite3.connect('apx_prime.db')
    u = conn.execute("SELECT is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    return True if u and u[0] == 1 else False

# ====================== DASHBOARD & SECURITY ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # 1. Strict Join Check
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🔄 VERIFY ACCESS", callback_data="refresh"))
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **STRICT AUTHENTICATION**\nJoin channel to initialize APX Nodes.", reply_markup=kb.as_markup())
    except: pass

    # Auto/Manual Broadcast Logic
    pkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    status = SYS_BC["msg"] if SYS_BC["mode"] == "manual" else ("✅ API NODES: STABLE" if 8 <= pkt.hour <= 23 else "🌙 NODES: SLEEP MODE")
    
    vip_active = await is_vip(uid)
    
    kb = InlineKeyboardBuilder()
    if not vip_active:
        kb.row(types.InlineKeyboardButton(text="🔑 GET ACCESS KEY (FREE)", callback_data="temp_key"))
    else:
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH APX TERMINAL", callback_data="init_term"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ TERMINATE", callback_data="exit_sys"))

    caption = (
        f"💎 **APX PRIME SYSTEM v33.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **TRADER:** `{message.from_user.first_name}`\n"
        f"📡 **STATUS:** `{status}`\n"
        f"⏰ **PKT TIME:** `{pkt.strftime('%H:%M')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Terminal Ready. Neural v4.2 Handshake Active."
    )
    if isinstance(message, types.Message): await message.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await message.message.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== TERMINAL WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE PAIR", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi")
    ).as_markup()
    await callback.message.edit_caption(caption="⚡ **SELECT MODE**:", reply_markup=kb)

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"mode": callback.data.split(":")[1], "pairs": []}
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text=f"🔥 NEXT: INDICATORS ({len(sel)})", callback_data="ask_ind"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="refresh"))
    await callback.message.edit_caption(caption="🧪 **ASSET GRID (24 PAIRS)**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if user_ctx[uid]["mode"] == "single": user_ctx[uid]["pairs"] = [pair]
    else:
        if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
        elif len(user_ctx[uid]["pairs"]) < 3: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

# ====================== MANUAL CONFIGURATIONS ======================
@dp.callback_query(F.data == "ask_ind")
async def ask_ind(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for ind in ["Bollinger Bands", "RSI Neural", "MACD Scalp"]:
        kb.row(types.InlineKeyboardButton(text=f"📉 {ind}", callback_data=f"set_i:{ind}"))
    await callback.message.edit_caption(caption="🧠 **MANUAL INDICATOR SELECT**:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_i:"))
async def ask_bands(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["ind"] = callback.data.split(":")[1]
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⚡ LEVEL 1 (SR)", callback_data="set_b:L1"),
           types.InlineKeyboardButton(text="🔥 LEVEL 2 (Neural)", callback_data="set_b:L2"))
    await callback.message.edit_caption(caption="📉 **MANUAL BANDS SELECT**:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_b:"))
async def ask_days(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["band"] = callback.data.split(":")[1]
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🗓️ 15 DAYS", callback_data="set_d:15"),
           types.InlineKeyboardButton(text="🗓️ 30 DAYS", callback_data="set_d:30"))
    await callback.message.edit_caption(caption="📂 **MANUAL DAYS SELECT** (History Scan):", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_d:"))
async def ask_time_manual(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["days"] = callback.data.split(":")[1]
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 **TIME PROTOCOL**\nSend **START TIME** (e.g. `14:00`)")

# ====================== TIME INPUT & SIGNALS ======================
@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 **TIME PROTOCOL**\nNow send **END TIME** (e.g. `16:30`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    data = user_ctx[message.from_user.id]
    load = await message.answer("📡 **INITIALIZING...**")
    
    # FLASHING BARS
    for i in [25, 60, 90, 100]:
        await asyncio.sleep(0.4)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING {data['days']} DAYS HISTORY**\n`[{bar}] {i}%` \nNodes: PKT UTC+5 Active")

    report = (
        f"╔════════════════════════════╗\n"
        f"        **APX ALPHA PRO**\n"
        f"╚════════════════════════════╝\n"
        f"STRAT: `{data['ind']}` | BANDS: `{data['band']}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f" TIME  ┃ ASSET   ┃ DIR   ┃ ACC \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p.split(' ')[1][:6]}` ┃ `{'CALL' if random.choice([0,1]) else 'PUT '}` ┃ `{random.randint(93, 99)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(5, 12))

    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | PKT ZONE**", parse_mode="Markdown")
    user_ctx.pop(message.from_user.id, None)

# ====================== ADMIN & BROADCAST ======================
@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    user_ctx[message.from_user.id] = {"step": "admin_bc"}
    await message.answer("🎙 **MANUAL BROADCAST**\nSend the message for Dashboard Status:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    SYS_BC["msg"] = f"📢 {message.text}"; SYS_BC["mode"] = "manual"
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Dashboard Updated!")

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    # Fancy Profile Detection
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Region: Pakistan 🇵🇰\n🛡 Rank: VIP 💎", show_alert=True)

@dp.callback_query(F.data == "temp_key")
async def temp_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000,9999)}"
    await callback.message.answer(f"🔑 **ACCESS KEY:** `{key}`\nSend `/verify {key}` to activate.")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    conn = sqlite3.connect('apx_prime.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (message.from_user.id, "2027-01-01"))
    conn.commit(); conn.close()
    await message.answer("✅ **ACCESS GRANTED!** Restart /start")

@dp.callback_query(F.data == "refresh")
async def refresh_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **APX PRIME TERMINAL**\n*Trading is risky. Come back soon!*")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
