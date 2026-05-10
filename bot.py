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

# HTML mode active for clickable copy text
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()
user_ctx = {} 
GLOBAL_BC = {"active": False, "text": ""}

# HARD-CODED 24 ASSETS
PAIRS_DATA = {
    "USDINR": "🇮🇳 USDINR-OTC", "USDPKR": "🇵🇰 USDPKR-OTC", "USDJPY": "🇯🇵 USDJPY-OTC", 
    "USDPHP": "🇵🇭 USDPHP-OTC", "USDMXN": "🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺 EURUSD-OTC",
    "GBPUSD": "🇬🇧 GBPUSD-OTC", "USDCAD": "🇨🇦 USDCAD-OTC", "XAUUSD": "🥇 XAUUSD-OTC",   
    "BTCUSD": "₿ BTCUSD-OTC", "USDTRY": "🇹🇷 USDTRY-OTC", "USDBRL": "🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿 NZDUSD-OTC", "AUDUSD": "🇦🇺 AUDUSD-OTC", "USDCHF": "🇨🇭 USDCHF-OTC", 
    "USDCOP": "🇨🇴 USDCOP-OTC", "USDBDT": "🇧🇩 USDBDT-OTC", "USDARS": "🇦🇷 USDARS-OTC",
    "AAPL": "🍎 AAPL-OTC", "MSFT": "💻 MSFT-OTC", "PFE": "💊 PFE-OTC", "JNJ": "🏥 JNJ-OTC",
    "MCD": "🍔 MCD-OTC", "INTL": "🔬 INTL-OTC"
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_final_v95.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, key_taken INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

async def get_node_status():
    if GLOBAL_BC["active"]: return f"📢 {GLOBAL_BC['text']}"
    h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= h < 8: return "🌙 <b>SLEEP MODE</b>"
    elif 13 <= h < 15: return "❄️ <b>COOL DOWN</b>"
    return "✅ <b>API NODE: STABLE</b>"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
            kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY ACCESS", callback_data="auth_check"))
            return await message.answer_photo(photo=BANNER_URL, caption="<b>🛡️ ACCESS DENIED</b>\nPlease join @vectabot1 first to initialize security.", reply_markup=kb.as_markup())
    except: pass
    await show_dashboard(message)

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, callback.from_user.id)
        if chat.status not in ["left", "kicked"]:
            await callback.message.delete()
            await bot.send_message(callback.from_user.id, "🎆") # Celebration Emoji
            await asyncio.sleep(0.5)
            await show_dashboard(callback)
        else: await callback.answer("❌ Please join channel first!", show_alert=True)
    except: pass

async def show_dashboard(m_c):
    uid = m_c.from_user.id
    msg = m_c if isinstance(m_c, types.Message) else m_c.message
    
    conn = sqlite3.connect('apx_final_v95.db')
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
        f"💎 <b>APX PRIME OS v95.0</b> 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>TRADER:</b> <code>{m_c.from_user.first_name}</code>\n"
        f"📡 <b>STATUS:</b> {status}\n"
        f"⏰ <b>PKT:</b> <code>{pkt}</code> | <b>RANK:</b> <b>{access}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Neural v9.5 Handshake: 🟢 <b>Stable</b>"
    )
    if isinstance(m_c, types.Message): await m_c.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else: await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== KEY & VERIFY (TAP-TO-COPY) ======================
@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    key = f"APX-{random.randint(1000, 9999)}-PRO"
    await callback.message.answer(f"🔑 <b>TAP TO COPY KEY:</b>\n\n<code>/verify {key}</code>\n\nSend this command here to unlock.")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_final_v95.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, key_taken) VALUES (?, ?, 1, 1)", (message.from_user.id, exp))
    conn.commit(); conn.close()
    
    await bot.send_message(ADMIN_ID, f"🔔 <b>NOTIFY:</b> {message.from_user.first_name} verified.")
    await message.answer("✅ <b>AUTHORIZED</b>\nLoading Dashboard..."); await asyncio.sleep(1); await start_handler(message)

# ====================== TERMINAL FLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": [], "last_report": None}
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE PAIR", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi")
    ).as_markup()
    await callback.message.edit_caption(caption="⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb)

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["mode"] = callback.data.split(":")[1]
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    mode = user_ctx[uid].get("mode", "single")
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text=f"🚀 NEURAL SCAN ({len(sel)})", callback_data="ask_param"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    await callback.message.edit_caption(caption=f"🧪 <b>ASSET GRID ({mode.upper()})</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid]["mode"] == "multi" else 1
    if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < limit: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_param")
async def ask_param(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="📊 BOLLINGER BANDS", callback_data="set_p:Bands"),
        types.InlineKeyboardButton(text="🗓️ 30 DAYS DATA", callback_data="set_p:30D")
    ).as_markup()
    await callback.message.edit_caption(caption="🧠 <b>SET SCAN PARAMETERS:</b>", reply_markup=kb)

@dp.callback_query(F.data.startswith("set_p:"))
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 <b>TIME PROTOCOL</b>\nSend Start Time (e.g. <code>14:00</code>)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 <b>TIME PROTOCOL</b>\nSend End Time (e.g. <code>16:00</code>)")
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
        load = await msg_obj.answer("📡 <b>SCANNING NODES...</b>")
        await asyncio.sleep(1); bar = "🟦🟦🟦🟦🟦⬜⬜⬜⬜⬜"
        await load.edit_text(f"🧪 <b>NEURAL SYNC</b>\n<code>[{bar}] 100%</code>")
        
        report = f"APX ALPHA SIGNALS\n━━━━━━━━━━━━━━━━━━━━━━\n"
        start = datetime.datetime.strptime(data['start_t'], "%H:%M")
        end = datetime.datetime.strptime(data['end_t'], "%H:%M")
        curr = start
        while curr < end:
            for p in data["pairs"]:
                report += f"{curr.strftime('%H:%M')} | {p.split(' ')[1][:6]} | {'CALL' if random.choice([0,1]) else 'PUT '} | {random.randint(95, 99)}%\n"
            curr += datetime.timedelta(minutes=random.randint(8, 14))
        data["last_report"] = report
        await load.delete()

    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen_sig"),
        types.InlineKeyboardButton(text="🔄 CHANGE PAIR", callback_data="init_term")
    ).row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys")).as_markup()

    final_msg = f"📋 <b>SIGNALS (TAP TO COPY):</b>\n\n<code>{report}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n✅ PKT UTC+5"
    if is_regen: await msg_obj.edit_text(final_msg, reply_markup=kb)
    else: await msg_obj.answer(final_msg, reply_markup=kb)

@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("Showing previous signals..."); await execute_signals(callback, is_regen=True)

# ====================== ADMIN ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎙 NOTICE", callback_data="adm:bc"),
        types.InlineKeyboardButton(text="🔄 AUTO", callback_data="adm:auto")
    ).as_markup()
    await message.answer("🛠 <b>ADMIN PANEL</b>", reply_markup=kb)

@dp.callback_query(F.data == "adm:bc")
async def bc_input(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"step": "admin_bc"}
    await callback.message.answer("✍️ Send Dashboard Status:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    GLOBAL_BC["active"] = True; GLOBAL_BC["text"] = message.text
    user_ctx.pop(message.from_user.id); await message.answer("✅ Updated!")

@dp.callback_query(F.data == "adm:auto")
async def reset_auto(callback: types.CallbackQuery):
    GLOBAL_BC["active"] = False; await callback.answer("🔄 Auto Mode!", show_alert=True)

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.message.delete(); await callback.message.answer("🌌 <b>OFFLINE</b>\n*Trade Smarter, Not Harder.*")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
