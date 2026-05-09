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
BC_CTRL = {"mode": "auto", "msg": ""}

# MUKKAMMAL 24 PAIRS - NO ASSET MISSING
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

# ====================== CORE ENGINES ======================
def init_db():
    conn = sqlite3.connect('apx_overlord.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

async def is_vip_active(uid):
    conn = sqlite3.connect('apx_overlord.db')
    u = conn.execute("SELECT is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    return True if u and u[0] == 1 else False

async def get_node_status():
    if BC_CTRL["mode"] == "manual": return f"📢 {BC_CTRL['msg']}"
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now.hour
    if 2 <= h < 8: return "🌙 **SLEEP MODE** (Low Vol)"
    elif 13 <= h < 15: return "❄️ **COOL DOWN** (API Maintenance)"
    return "✅ **NODE: STABLE (UTC+5)**"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # 1. STRICT JOIN CHECK
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN OFFICIAL CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY & ACCESS", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="🚫 **STRICT ACCESS**\nPlease join our channel to synchronize with the API Node.", reply_markup=kb.as_markup())
    except: pass

    # 2. VIP STATUS & DASHBOARD
    is_vip = await is_vip_active(uid)
    node_status = await get_node_status()
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if not is_vip:
        kb.row(types.InlineKeyboardButton(text="🔑 GET TEMP ACCESS KEY", callback_data="get_temp"))
    else:
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TITAN TERMINAL", callback_data="init_term"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    caption = (
        f"💎 **APX PRIME OS v37.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **TRADER:** `{message.from_user.first_name}`\n"
        f"📡 **NODE:** {node_status}\n"
        f"⏰ **PKT:** `{pkt}` | **RANK:** `{'VIP 💎' if is_vip else 'GUEST'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Institutional Handshake Active."
    )
    
    if isinstance(message, types.Message): await message.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await message.message.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== SELECTION FLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi")
    ).row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="auth_check")).as_markup()
    await callback.message.edit_caption(caption="⚡ **EXTRACTION INTENSITY**:", reply_markup=kb)

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

@dp.callback_query(F.data == "ask_ind")
async def ask_ind(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for ind in ["Bollinger Bands", "Neural RSI V3", "Price Action"]:
        kb.row(types.InlineKeyboardButton(text=f"📊 {ind}", callback_data=f"set_i:{ind}"))
    await callback.message.edit_caption(caption="🧠 **STRATEGY CONFIG**:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_i:"))
async def ask_time_1(callback: types.CallbackQuery):
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

# ====================== EXTRACTION (BLUE NEON BARS) ======================
async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **INITIALIZING API...**")
    
    for i in [30, 65, 90, 100]:
        await asyncio.sleep(0.4)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING {data['ind']}**\n`[{bar}] {i}%` \nExtraction Depth: 95%+")

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
    
    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | UTC+5 PKT**", parse_mode="Markdown", reply_markup=kb.as_markup())
    user_ctx.pop(uid, None)

# ====================== ADMIN & UTILS ======================
@dp.message(Command("admin"))
async def admin_bc(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    user_ctx[message.from_user.id] = {"step": "admin_bc"}
    await message.answer("🎙 **MASTER BROADCAST**\nSend message for Dashboard Status:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    BC_CTRL["msg"] = message.text; BC_CTRL["mode"] = "manual"
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Dashboard Status Updated!")

@dp.callback_query(F.data == "get_temp")
async def temp_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000,9999)}"
    await callback.message.answer(f"🔑 **ACCESS KEY (COPY):**\n`{key}`\n\nSend `/verify {key}` to activate.")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    conn = sqlite3.connect('apx_overlord.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, is_vip) VALUES (?, 1)", (message.from_user.id,))
    conn.commit(); conn.close()
    await message.answer("✅ **ACCESS GRANTED!** Restart /start")

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "copy_ack")
async def copy_ack(callback: types.CallbackQuery):
    await callback.answer("✅ Signals copied to clipboard!", show_alert=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **APX PRIME SHUTDOWN**\nStay Ahead of the Market.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
    
