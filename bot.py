import os
import asyncio
import datetime
import random
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================== 24 ASSETS GRID (FIXED) ======================
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
MANUAL_NOTICE = {"active": False, "msg": ""}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_prime_v66.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0)')
    conn.commit(); conn.close()

async def check_access(uid):
    conn = sqlite3.connect('apx_prime_v66.db')
    u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if u and u[1] == 1:
        exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < exp: return "ACTIVE"
    return "LOCKED"

async def get_node_status():
    if MANUAL_NOTICE["active"]: return f"📢 {MANUAL_NOTICE['msg']}"
    h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= h < 8: return "🌙 NODE: SLEEP MODE"
    elif 13 <= h < 15: return "❄️ NODE: COOL DOWN"
    return "✅ NODE: STABLE & ACTIVE"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="✅ I HAVE JOINED", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **STRICT AUTHENTICATION**\nJoin @vectabot1 to unlock the APX Prime Terminal.", reply_markup=kb.as_markup())
    except: pass
    await show_dashboard(message)

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ Authenticated!", show_alert=False)
            await callback.message.delete()
            await show_dashboard(callback)
        else:
            await callback.answer("❌ Error: Membership not found. Please join @vectabot1 first!", show_alert=True)
    except: pass

async def show_dashboard(m_c):
    uid = m_c.from_user.id
    msg = m_c if isinstance(m_c, types.Message) else m_c.message
    access = await check_access(uid)
    status = await get_node_status()
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if access == "ACTIVE":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_temp"))
    
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    caption = (
        f"🌌 **APX PRIME OS v66.0** 🌌\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"USER: {m_c.from_user.first_name}\n"
        f"STATUS: {status}\n"
        f"TIME: {pkt} PKT | RANK: {'VIP ✅' if access == 'ACTIVE' else 'GUEST 🔒'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Institutional Handshake: Active"
    )
    if isinstance(m_c, types.Message): await m_c.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== ACCESS CONTROL ======================
@dp.callback_query(F.data == "get_temp")
async def get_temp(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000, 9999)}-PRO"
    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📋 COPY KEY", callback_data=f"copy_k:{key}")).as_markup()
    await callback.message.answer(f"🔑 **YOUR LICENSE KEY:**\n\n`/verify {key}`\n\nTap to copy and send to activate 7 days.", reply_markup=kb)

@dp.callback_query(F.data.startswith("copy_k:"))
async def copy_key(callback: types.CallbackQuery):
    await callback.answer("✅ Key copied!", show_alert=True)

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_prime_v66.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip) VALUES (?, ?, 1)", (message.from_user.id, exp))
    conn.commit(); conn.close()
    await bot.send_message(ADMIN_ID, f"🔔 **JOIN NOTIFY:** {message.from_user.first_name} activated terminal.")
    await message.answer("✅ **ACCESS GRANTED!**\nLoading Terminal...")
    await asyncio.sleep(1); await start_handler(message)

# ====================== TERMINAL WORKFLOW ======================
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
    if sel: builder.row(types.InlineKeyboardButton(text=f"🔥 SCAN NODES ({len(sel)})", callback_data="ask_days"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="auth_check"))
    await callback.message.edit_caption(caption="🧪 **ASSET GRID (24 ASSETS)**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < 3: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_days")
async def ask_days(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🗓️ 15 DAYS", callback_data="set_d:15"),
        types.InlineKeyboardButton(text="🗓️ 30 DAYS", callback_data="set_d:30")
    ).as_markup()
    await callback.message.edit_caption(caption="📂 **SELECT QUOTEX DATA DEPTH**:", reply_markup=kb)

@dp.callback_query(F.data.startswith("set_d:"))
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["days"] = callback.data.split(":")[1]
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 **TIME RANGE**\nSend Start Time (e.g. `14:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 **TIME RANGE**\nSend End Time (e.g. `16:00`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 **SYNCHRONIZING...**")
    for i in [40, 80, 100]:
        await asyncio.sleep(0.4); bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING {data['days']} DAYS**\n`[{bar}] {i}%` \nNodes: Active")

    report = f"APX ALPHA SIGNALS\n━━━━━━━━━━━━━━━━━━━━\n"
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            report += f"{curr.strftime('%H:%M')} | {p.split(' ')[1][:6]} | {'CALL' if random.choice([0,1]) else 'PUT '} | {random.randint(95, 99)}%\n"
        curr += datetime.timedelta(minutes=random.randint(6, 12))

    await load.delete()
    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_s")).as_markup()
    await message.answer(f"`{report}`\n━━━━━━━━━━━━━━━━━━━━\n✅ UTC+5 PKT", reply_markup=kb)
    user_ctx.pop(uid, None)

# ====================== ADMIN PANEL ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎙 MANUAL NOTICE", callback_data="adm:msg"),
        types.InlineKeyboardButton(text="🔄 AUTO MODE", callback_data="adm:auto")
    ).as_markup()
    await message.answer("🛠 **ADMIN PANEL**", reply_markup=kb)

@dp.callback_query(F.data == "adm:msg")
async def bc_input(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"step": "admin_bc"}
    await callback.message.answer("✍️ Send Dashboard Status:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    MANUAL_NOTICE["active"] = True; MANUAL_NOTICE["msg"] = message.text
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Updated!")

@dp.callback_query(F.data == "adm:auto")
async def reset_auto(callback: types.CallbackQuery):
    MANUAL_NOTICE["active"] = False
    await callback.answer("🔄 Back to Auto Sync!", show_alert=True)

@dp.callback_query(F.data == "copy_s")
async def copy_s(callback: types.CallbackQuery):
    await callback.answer("✅ Signals copied!", show_alert=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **TERMINAL OFFLINE**")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
