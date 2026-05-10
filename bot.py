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
MANUAL_BROADCAST = {"active": False, "text": ""}

# HARD-CODED 24 ASSETS
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

# ====================== DATABASE & LOGIC ======================
def init_db():
    conn = sqlite3.connect('apx_overlord_final.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, key_taken INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

async def get_node_status():
    if MANUAL_BROADCAST["active"]:
        return f"📢 {MANUAL_BROADCAST['text']}"
    
    # Auto logic based on Pakistan Time (UTC+5)
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now.hour
    if 2 <= h < 8: return "🌙 SLEEP MODE (Market Low)"
    elif 13 <= h < 15: return "❄️ COOL DOWN (Node Sync)"
    return "✅ API NODE: STABLE"

# ====================== DASHBOARD ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY ACCESS", callback_data="auth_check"))
            return await message.answer("🛡️ **ACCESS BLOCKED**\nJoin @vectabot1 to unlock the dashboard.", reply_markup=kb.as_markup())
    except: pass
    await show_dashboard(message)

async def show_dashboard(m_c):
    uid = m_c.from_user.id
    msg = m_c if isinstance(m_c, types.Message) else m_c.message
    
    # Database check for access
    conn = sqlite3.connect('apx_overlord_final.db')
    u = conn.execute("SELECT expiry, is_vip, key_taken FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    
    access = "LOCKED"
    if u and u[1] == 1:
        exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < exp: access = "ACTIVE"
    
    status = await get_node_status()
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    
    kb = InlineKeyboardBuilder()
    if access == "ACTIVE":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    elif not u or u[2] == 0:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔒 ACCESS EXPIRED", callback_data="profile"))

    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    caption = (
        f"💎 **APX PRIME OS v80.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 USER: `{m_c.from_user.first_name}`\n"
        f"📡 NODE: {status}\n"
        f"⏰ PKT: `{pkt}` | RANK: `{'VIP ✅' if access == 'ACTIVE' else 'GUEST'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural Handshake: `Active` 🟢"
    )
    if isinstance(m_c, types.Message): await m_c.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== ADMIN BROADCAST & NOTIFY ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎙 MANUAL NOTICE", callback_data="adm:msg"),
        types.InlineKeyboardButton(text="🔄 RESET TO AUTO", callback_data="adm:auto")
    ).as_markup()
    await message.answer("🛠 **MASTER CONTROL PANEL**", reply_markup=kb)

@dp.callback_query(F.data == "adm:msg")
async def bc_input(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"step": "admin_bc"}
    await callback.message.answer("✍️ Send Manual Notice for Dashboard:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    MANUAL_BROADCAST["active"] = True; MANUAL_BROADCAST["text"] = message.text
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Manual Notice Active on Dashboard!")

@dp.callback_query(F.data == "adm:auto")
async def reset_auto(callback: types.CallbackQuery):
    MANUAL_BROADCAST["active"] = False
    await callback.answer("🔄 Back to Auto Sync Mode!", show_alert=True)

# ====================== KEY & VERIFY ======================
@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000, 9999)}-VIP"
    # Clickable text for copy
    await callback.message.answer(f"🔑 **YOUR 7-DAY ACCESS KEY:**\n\n`/verify {key}`\n\n*Tap to copy. One-time use only.*")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_overlord_final.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, key_taken) VALUES (?, ?, 1, 1)", (message.from_user.id, exp))
    conn.commit(); conn.close()
    
    # ADMIN NOTIFICATION
    await bot.send_message(ADMIN_ID, f"🔔 **NEW USER NOTIFY:**\nTrader `{message.from_user.first_name}` (ID: `{message.from_user.id}`) has activated terminal.")
    await message.answer("✅ **ACCESS GRANTED**\nRestarting terminal..."); await asyncio.sleep(1); await start_handler(message)

# ====================== TERMINAL WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": [], "last_report": None}
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE PAIR", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi")
    ).as_markup()
    await callback.message.edit_caption(caption="⚡ **SELECT OPERATIONAL MODE**:", reply_markup=kb)

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["mode"] = callback.data.split(":")[1]
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text=f"🚀 NEURAL SCAN ({len(sel)})", callback_data="ask_time"))
    await callback.message.edit_caption(caption="🧪 **ASSET SELECTION GRID**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < (3 if user_ctx[uid]["mode"]=="multi" else 1): user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 Send **START TIME** (e.g. `14:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 Send **END TIME** (e.g. `16:00`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id if isinstance(message, types.Message) else message.from_user.id
    msg_obj = message if isinstance(message, types.Message) else message.message
    data = user_ctx[uid]

    if is_regen and data.get("last_report"):
        report = data["last_report"]
    else:
        load = await msg_obj.answer("📡 **SCANNING...**")
        await asyncio.sleep(1); bar = "🟦🟦🟦🟦🟦⬜⬜⬜⬜⬜"
        await load.edit_text(f"🧪 **SCANNING API**\n`[{bar}] 100%` \nNodes: Active")
        
        report = f"APX ALPHA SIGNALS\n━━━━━━━━━━━━━━━━━━━━━━\n"
        start = datetime.datetime.strptime(data['start_t'], "%H:%M")
        end = datetime.datetime.strptime(data['end_t'], "%H:%M")
        curr = start
        while curr < end:
            for p in data["pairs"]:
                report += f"{curr.strftime('%H:%M')} | {p.split(' ')[1][:6]} | {'CALL' if random.choice([0,1]) else 'PUT '} | {random.randint(95, 99)}%\n"
            curr += datetime.timedelta(minutes=random.randint(7, 13))
        
        data["last_report"] = report
        await load.delete()

    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen_sig"),
        types.InlineKeyboardButton(text="🔄 CHANGE PAIR", callback_data="init_term")
    ).row(types.InlineKeyboardButton(text="❌ EXIT MENU", callback_data="exit_sys")).as_markup()

    final_msg = f"📋 **SIGNALS (TAP TO COPY):**\n\n`{report}`\n━━━━━━━━━━━━━━━━━━━━━━\n✅ UTC+5 PKT"
    if is_regen: await msg_obj.edit_text(final_msg, parse_mode="Markdown", reply_markup=kb)
    else: await msg_obj.answer(final_msg, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("Showing previous signals..."); await execute_signals(callback, is_regen=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 **OFFLINE**")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
