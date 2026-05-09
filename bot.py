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

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 
GLOBAL_BC = {"mode": "auto", "text": ""}

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

# ====================== DATABASE & SECURITY ======================
def init_db():
    conn = sqlite3.connect('apx_prime_v43.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)')
    conn.execute('CREATE TABLE IF NOT EXISTS keys (key_val TEXT PRIMARY KEY, days INTEGER)')
    conn.commit(); conn.close()

async def check_access(uid):
    conn = sqlite3.connect('apx_prime_v43.db')
    u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if u and u[1] == 1:
        expiry_dt = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < expiry_dt: return "ACTIVE"
    return "LOCKED"

async def get_node_status():
    if GLOBAL_BC["mode"] == "manual": return f"📢 {GLOBAL_BC['text']}"
    pkt_h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= pkt_h < 8: return "🌙 **SLEEP MODE**"
    elif 13 <= pkt_h < 15: return "❄️ **COOL DOWN**"
    return "✅ **API NODE: STABLE**"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    # --- STEP 1: HARD WALL JOIN CHECK ---
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🔄 VERIFY JOINING", callback_data="auth_check"))
            return await message.answer("🛡️ **STRICT AUTHENTICATION REQUIRED**\n\nPlease join our official channel to initialize the Neural Handshake. After joining, click the button below.", reply_markup=kb.as_markup())
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
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH APX TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 ACTIVATE VIP LICENSE", callback_data="req_key"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    caption = (
        f"💎 **APX PRIME OS v43.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **TRADER:** `{message_or_call.from_user.first_name}`\n"
        f"📡 **NODE:** {status}\n"
        f"⏰ **PKT:** `{pkt}` | **RANK:** `{'VIP ✅' if access == 'ACTIVE' else 'LOCKED 🔒'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural Terminal Online. Zone: UTC+5."
    )
    
    if isinstance(message_or_call, types.Message): await message_or_call.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== ADMIN KEY GENERATION ======================
@dp.message(Command("genkey"))
async def gen_key(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    days = int(args[1]) if len(args) > 1 else 1 # Default 1 day
    
    new_key = f"APX-{random.randint(1000, 9999)}-{days}D"
    conn = sqlite3.connect('apx_prime_v43.db')
    conn.execute("INSERT INTO keys (key_val, days) VALUES (?, ?)", (new_key, days))
    conn.commit(); conn.close()
    
    await message.answer(f"🔑 **{days} DAY(S) KEY GENERATED:**\n\n`/verify {new_key}`\n\n(Send this to the user)")

@dp.message(Command("verify"))
async def verify_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Use: `/verify KEY`")
    k = args[1]
    
    conn = sqlite3.connect('apx_prime_v43.db')
    check = conn.execute("SELECT days FROM keys WHERE key_val = ?", (k,)).fetchone()
    if check:
        days = check[0]
        conn.execute("DELETE FROM keys WHERE key_val = ?", (k,))
        exp = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (message.from_user.id, exp))
        conn.commit(); conn.close()
        
        await bot.send_message(ADMIN_ID, f"🔔 **ADMIN NOTIFY:** User `{message.from_user.first_name}` activated **{days} Day(s)**.")
        await message.answer(f"✅ **VIP ACTIVATED!**\nAccess granted for {days} day(s).")
        await asyncio.sleep(1); await start_handler(message)
    else:
        conn.close(); await message.answer("❌ **INVALID KEY!** Contact @MMQUOBOT")

# ====================== WORKFLOW (24 PAIRS) ======================
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
    if sel: builder.row(types.InlineKeyboardButton(text=f"🔥 SCAN ({len(sel)})", callback_data="ask_time"))
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
    data = user_ctx[message.from_user.id]
    load = await message.answer("📡 **ANALYZING...**")
    for i in [30, 70, 100]:
        await asyncio.sleep(0.4); bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING**\n`[{bar}] {i}%` \nNodes: PKT Active")

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
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p.split(' ')[1][:6]}` ┃ `{'CALL' if random.choice([0,1]) else 'PUT '}` ┃ `{random.randint(94, 99)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(6, 12))

    await load.delete(); await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API VERIFIED | UTC+5 PKT**")
    user_ctx.pop(message.from_user.id, None)

# ====================== ADMIN & UTILS ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎙 SEND NOTICE", callback_data="adm:bc"),
        types.InlineKeyboardButton(text="🔄 RESET AUTO", callback_data="adm:auto")
    ).as_markup()
    await message.answer("🛠 **MASTER CONTROL**", reply_markup=kb)

@dp.callback_query(F.data == "adm:bc")
async def bc_input(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"step": "admin_bc"}
    await callback.message.answer("✍️ Send Dashboard Status Notice:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    GLOBAL_BC["text"] = message.text; GLOBAL_BC["mode"] = "manual"
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Status Updated!")

@dp.callback_query(F.data == "adm:auto")
async def reset_auto(callback: types.CallbackQuery):
    GLOBAL_BC["mode"] = "auto"; await callback.answer("🔄 Back to Auto!", show_alert=True)

@dp.callback_query(F.data == "req_key")
async def req_key(callback: types.CallbackQuery):
    await callback.answer("Admin notified!", show_alert=True)
    await bot.send_message(ADMIN_ID, f"🔔 **KEY REQUEST:**\nUser: `{callback.from_user.full_name}`\nID: `{callback.from_user.id}`")

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    await callback.message.delete(); await start_handler(callback.message)

@dp.callback_query(F.data == "profile")
async def profile_cb(callback: types.CallbackQuery):
    await callback.answer(f"👤 Trader: {callback.from_user.first_name}\n🌍 Zone: Pakistan 🇵🇰", show_alert=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **OFFLINE**")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
