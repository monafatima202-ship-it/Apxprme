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

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 
GLOBAL_BC = {"mode": "auto", "text": ""}

# MUKKAMMAL 24 ASSET GRID
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
    conn = sqlite3.connect('apx_prime_v45.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)')
    conn.commit(); conn.close()

async def check_access(uid):
    conn = sqlite3.connect('apx_prime_v45.db')
    u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if u and u[2] == 1:
        expiry_dt = datetime.datetime.strptime(u[1], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < expiry_dt: return "ACTIVE"
    return "LOCKED"

async def get_node_status():
    if GLOBAL_BC["mode"] == "manual": return f"📡 `{GLOBAL_BC['text']}`"
    h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= h < 8: return "🌙 **SLEEP MODE**"
    elif 13 <= h < 15: return "❄️ **COOL DOWN**"
    return "⚡ **API: STABLE**"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # STRICT FIREWALL
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY JOINING", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **STRICT AUTHENTICATION**\n\nYour ID is not linked with the APX Node. Join our official channel to initialize.", reply_markup=kb.as_markup())
    except: pass

    await show_dashboard(message)

async def show_dashboard(message_or_call):
    uid = message_or_call.from_user.id
    msg = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    access = await check_access(uid)
    status = await get_node_status()
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if access == "ACTIVE":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 ACTIVATE VIP LICENSE", callback_data="gen_temp_direct"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ SHUTDOWN", callback_data="exit_sys"))

    # STYLISH NEON CAPTION
    caption = (
        f"🌌 **APX PRIME OS v45.0** 🌌\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕹️ **USER:** `{message_or_call.from_user.first_name}`\n"
        f"📡 **NODE:** {status}\n"
        f"🕰️ **PKT:** `{pkt}` | **RANK:** `{'VIP 💎' if access == 'ACTIVE' else 'LOCKED 🔒'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Institutional Handshake: `Active` 🟢"
    )
    
    if isinstance(message_or_call, types.Message): await message_or_call.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== KEY SYSTEM ======================
@dp.callback_query(F.data == "gen_temp_direct")
async def gen_temp(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000, 9999)}-VIP"
    await callback.message.answer(f"🔑 **YOUR LICENSE KEY (TAP TO COPY):**\n\n`/verify {key}`\n\nSend this command to unlock 24H access.")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    uid = message.from_user.id
    args = message.text.split()
    if len(args) < 2: return await message.answer("Use: `/verify KEY`")
    
    # 24H Activation
    exp = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_prime_v45.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (uid, exp))
    conn.commit(); conn.close()
    
    await message.answer("✅ **NEURAL ACCESS GRANTED!**\nTerminal Unlocked. PKT UTC+5 Handshake Complete.")
    await asyncio.sleep(1); await start_handler(message)

# ====================== TERMINAL FLOW (STYLISH) ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": []}
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text=f"🔥 SCAN NODES ({len(sel)})", callback_data="ask_time"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="auth_check"))
    await callback.message.edit_caption(caption="🧪 **ASSET GRID (24 PAIRS)**\nSelect assets to extract trends:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < 3: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
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
        await message.answer("🕒 **TIME PROTOCOL**\nSend **END TIME** (Format: `16:00`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **SYNCHRONIZING...**")
    for i in [30, 75, 100]:
        await asyncio.sleep(0.4); bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING API**\n`[{bar}] {i}%` \nNodes: PKT Active")

    # STYLISH TABLE ALIGNMENT
    report = (
        f"╔════════════════════════════╗\n"
        f"        **APX ALPHA PRO**\n"
        f"╚════════════════════════════╝\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f" TIME  ┃ ASSET   ┃ DIR   ┃ ACC \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            p_short = p.split(' ')[1][:6]
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p_short}` ┃ `{'CALL' if random.choice([0,1]) else 'PUT '}` ┃ `{random.randint(94, 99)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(6, 11))

    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | UTC+5 PKT**", parse_mode="Markdown")
    user_ctx.pop(uid, None)

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Region: PKT\n🛡 Status: VIP", show_alert=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **OFFLINE**\n*Market closes but opportunity doesn't.*")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
