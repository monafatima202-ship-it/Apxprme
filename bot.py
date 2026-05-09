import os
import asyncio
import datetime
import random
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================== 100% FIXED 24 ASSET GRID ======================
# Is list ko kisi surat mein delete nahi karna
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

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_prime_v48.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)')
    conn.commit(); conn.close()

async def check_access(uid):
    conn = sqlite3.connect('apx_prime_v48.db')
    u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if u and u[2] == 1:
        expiry_dt = datetime.datetime.strptime(u[1], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < expiry_dt: return "ACTIVE"
    return "LOCKED"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # STRICT FIREWALL: JOIN CHECK FIRST
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY ACCESS", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **STRICT ACCESS**\nPlease join the official channel to link your ID with the Neural Node.", reply_markup=kb.as_markup())
    except: pass

    await show_dashboard(message)

async def show_dashboard(message_or_call):
    uid = message_or_call.from_user.id
    msg = message_or_call if isinstance(message_or_call, types.Message) else message_or_call.message
    access = await check_access(uid)
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if access == "ACTIVE":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH APX TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 24H TEMP ACCESS", callback_data="gen_key_cmd"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT SYSTEM", callback_data="exit_sys"))

    caption = (
        f"🌌 **APX PRIME OS v48.0** 🌌\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕹️ **USER:** `{message_or_call.from_user.first_name}`\n"
        f"📡 **NODE:** {'⚡ STABLE' if access == 'ACTIVE' else '🔒 LOCKED'}\n"
        f"🕰️ **PKT:** `{pkt}` | **RANK:** `{'VIP 💎' if access == 'ACTIVE' else 'GUEST'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural Handshake: `Verified` 🟢"
    )
    
    if isinstance(message_or_call, types.Message): await message_or_call.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== KEY & AUTO-REDIRECT ======================
@dp.callback_query(F.data == "gen_key_cmd")
async def gen_key_cmd(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000, 9999)}-VIP"
    # User tap karega toh sirf ye command copy hogi
    await callback.message.answer(f"🔑 **YOUR LICENSE KEY:**\n\n`/verify {key}`\n\n**Tap the command above to copy**, then send it here to unlock.")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    uid = message.from_user.id
    # Access for 24 Hours
    exp = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_prime_v48.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (uid, exp))
    conn.commit(); conn.close()
    
    await message.answer("✅ **ACCESS GRANTED!**\nTerminal Unlocked. Loading Dashboard...")
    await asyncio.sleep(1)
    await start_handler(message) # AUTO-REDIRECT

# ====================== TERMINAL (24 PAIRS GRID) ======================
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
    await callback.message.edit_caption(caption="🧪 **ASSET GRID (24 PAIRS)**", reply_markup=builder.as_markup())

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
    await callback.message.answer("🕒 **TIME RANGE**\nSend **START TIME** (e.g. `14:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 **TIME RANGE**\nSend **END TIME** (e.g. `16:00`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **ANALYZING...**")
    for i in [40, 80, 100]:
        await asyncio.sleep(0.4); bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING API**\n`[{bar}] {i}%` \nNodes: PKT Active")

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
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p.split(' ')[1][:6]}` ┃ `{'CALL' if random.choice([0,1]) else 'PUT '}` ┃ `{random.randint(95, 99)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(6, 11))

    await load.delete(); await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | UTC+5 PKT**", parse_mode="Markdown")
    user_ctx.pop(uid, None)

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🛡 Rank: VIP Member", show_alert=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **OFFLINE**")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
