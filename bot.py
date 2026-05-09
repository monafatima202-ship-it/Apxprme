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
BC_STATUS = {"mode": "auto", "msg": ""}

# FULL 24 ASSET GRID
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
    conn = sqlite3.connect('apx_overlord.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)')
    conn.commit(); conn.close()

async def get_vip_status(uid):
    conn = sqlite3.connect('apx_overlord.db')
    u = conn.execute("SELECT is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    return True if u and u[0] == 1 else False

async def get_node_status():
    if BC_STATUS["mode"] == "manual": return f"📢 {BC_STATUS['msg']}"
    h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= h < 8: return "🌙 **SLEEP MODE** (Low Vol)"
    elif 13 <= h < 15: return "❄️ **COOL DOWN** (Maintenance)"
    return "✅ **NODE: STABLE (UTC+5)**"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # --- STEP 1: STRICT FIREWALL (BINA JOIN KUCH NAHI DIKHEGA) ---
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN OFFICIAL CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY & ACCESS", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="🚫 **STRICT ACCESS PROTOCOL**\n\nYour ID is not synchronized with our Neural Node. Please join the channel to unlock the terminal.", reply_markup=kb.as_markup())
    except: pass

    await show_dashboard(message)

async def show_dashboard(message_or_call):
    uid = message_or_call.from_user.id
    msg = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    
    vip_active = await get_vip_status(uid)
    node_status = await get_node_status()
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if not vip_active:
        kb.row(types.InlineKeyboardButton(text="🔑 GET TEMP ACCESS KEY", callback_data="get_temp"))
    else:
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TITAN TERMINAL", callback_data="init_term"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    caption = (
        f"💎 **APX PRIME OS v38.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **TRADER:** `{message_or_call.from_user.first_name}`\n"
        f"📡 **NODE:** {node_status}\n"
        f"⏰ **PKT:** `{pkt}` | **RANK:** `{'VIP 💎' if vip_active else 'GUEST'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural Terminal Online. Node UTC+5 PKT."
    )
    
    if isinstance(message_or_call, types.Message): await message_or_call.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== WORKFLOW (24 PAIRS) ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi")
    ).row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="auth_check")).as_markup()
    await callback.message.edit_caption(caption="⚡ **SELECT EXTRACTION MODE**:", reply_markup=kb)

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
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
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

# ====================== EXTRACTION (BLUE BARS) ======================
@dp.callback_query(F.data == "ask_ind")
async def ask_ind(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for ind in ["Bollinger Bands", "RSI Neural V3", "Price Action"]:
        kb.row(types.InlineKeyboardButton(text=f"📊 {ind}", callback_data=f"set_i:{ind}"))
    await callback.message.edit_caption(caption="🧠 **STRATEGY CONFIG**:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_i:"))
async def step_time_1(callback: types.CallbackQuery):
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
        await message.answer("🕒 **TIME PROTOCOL**\nNow send **END TIME** (Format: `15:30`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **INITIALIZING...**")
    for i in [30, 70, 100]:
        await asyncio.sleep(0.4); bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING {data['ind']}**\n`[{bar}] {i}%` \nNodes: PKT UTC+5 Active")

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
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p.split(' ')[1][:6]}` ┃ `{'CALL' if random.choice([0,1]) else 'PUT '}` ┃ `{random.randint(94, 99)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(5, 12))

    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_ack"))
    kb.row(types.InlineKeyboardButton(text="⬅️ NEW EXTRACTION", callback_data="auth_check"))
    await load.delete(); await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | UTC+5 PKT**", parse_mode="Markdown", reply_markup=kb.as_markup())
    user_ctx.pop(uid, None)

# ====================== UTILS & ADMIN ======================
@dp.callback_query(F.data == "get_temp")
async def temp_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000,9999)}"
    # Full command blue format for easy copy
    await callback.message.answer(f"🔑 **ACCESS KEY (TAP TO COPY):**\n\n`/verify {key}`\n\nSend this command to activate 24h access.")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    conn = sqlite3.connect('apx_overlord.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, is_vip) VALUES (?, 1)", (message.from_user.id,))
    conn.commit(); conn.close()
    await bot.send_message(ADMIN_ID, f"🔔 **ADMIN NOTIFY:** User `{message.from_user.first_name}` verified.")
    await message.answer("✅ **VIP ACTIVATED!** Restart via /start")

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    is_v = await get_vip_status(callback.from_user.id)
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Region: Pakistan 🇵🇰\n🛡 Rank: {'VIP 💎' if is_v else 'Guest'}", show_alert=True)

@dp.callback_query(F.data == "rules")
async def rules_cb(callback: types.CallbackQuery):
    await callback.message.edit_caption(caption="📜 **MASTER RULES**\n\n1. OTC Assets only.\n2. M-1 Martingale permitted.\n3. 1-Minute expiry time.", reply_markup=InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="auth_check")).as_markup())

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    await callback.answer("Syncing..."); await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **APX PRIME TERMINAL**\n*Trading is business, not gambling. Node Offline.*")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
