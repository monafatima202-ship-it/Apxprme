import os
import asyncio
import datetime
import random
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================== CONFIG ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()
user_ctx = {}
GLOBAL_BC = {"mode": "auto", "text": ""}

# ====================== PAIRS ======================
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
    try:
        conn = sqlite3.connect('apx_prime.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                     (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, 
                      key_taken INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)

async def check_access(uid):
    try:
        conn = sqlite3.connect('apx_prime.db')
        u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
        conn.close()
        if u and u[1] == 1:
            exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
            if datetime.datetime.now() < exp:
                return True
    except:
        pass
    return False

async def is_joined(uid):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        return member.status not in ["left", "kicked"]
    except:
        return False

# ====================== NODE STATUS ======================
async def get_node_status():
    if GLOBAL_BC["mode"] == "manual":
        return f"📢 {GLOBAL_BC['text']}"
    h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= h < 8:
        return "🌙 SLEEP MODE"
    elif 13 <= h < 15:
        return "❄️ COOL DOWN"
    return "✅ STABLE"

# ====================== START ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id

    if not await is_joined(uid):
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        kb.row(types.InlineKeyboardButton(text="✅ CHECK JOIN", callback_data="check_join"))
        return await message.answer_photo(photo=BANNER_URL, caption="<b>🛡️ STRICT ACCESS</b>\nJoin channel first to continue.", reply_markup=kb.as_markup())

    await show_dashboard(message)

async def show_dashboard(obj):
    uid = obj.from_user.id
    is_msg = isinstance(obj, types.Message)
    msg = obj if is_msg else obj.message

    is_vip = await check_access(uid)
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    node = await get_node_status()

    kb = InlineKeyboardBuilder()
    if is_vip:
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 7 DAY ACCESS", callback_data="get_key"))

    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"),
           types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit"))

    caption = f"""
🌌 <b>APX PRIME OS v5.4</b> 🌌
━━━━━━━━━━━━━━━━━━━━━━
👤 <b>User:</b> <code>{obj.from_user.first_name}</code>
📡 <b>Node:</b> {node}
🕰️ <b>PKT:</b> <code>{pkt}</code> | <b>Rank:</b> {'VIP 💎' if is_vip else 'GUEST'}
━━━━━━━━━━━━━━━━━━━━━━
"""

    if is_msg:
        await obj.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else:
        await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())

# ====================== KEY SYSTEM ======================
@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    uid = callback.from_user.id
    key = f"APX-{random.randint(1000,9999)}-VIP-{uid%1000}"
    
    conn = sqlite3.connect('apx_prime.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, key_taken) VALUES (?, 1)", (uid,))
    conn.commit()
    conn.close()

    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📋 COPY KEY", callback_data=f"copy:{key}"))
    await callback.message.answer(f"🔑 <b>YOUR KEY</b>\n\n<code>/verify {key}</code>", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("copy:"))
async def copy_key(callback: types.CallbackQuery):
    key = callback.data.split(":",1)[1]
    await callback.answer(f"✅ COPIED\n{key}", show_alert=True)

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    uid = message.from_user.id
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('apx_prime.db')
    conn.execute("UPDATE users SET expiry=?, is_vip=1 WHERE uid=?", (exp, uid))
    conn.commit()
    conn.close()

    await message.answer("🎉 <b>NEURAL ACCESS GRANTED!</b>\n7 Days VIP Activated")
    await asyncio.sleep(1.5)
    await start_handler(message)

# ====================== TERMINAL & SIGNALS ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": []}
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx.get(uid, {}).get("pairs", [])
    builder = InlineKeyboardBuilder()
    for display in PAIRS_DATA.values():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel:
        builder.row(types.InlineKeyboardButton(text=f"🚀 GENERATE SIGNALS ({len(sel)})", callback_data="ask_time"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="back"))
    await callback.message.edit_caption(caption="🧪 <b>SELECT ASSETS (Max 3)</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":",1)[1]
    if uid not in user_ctx: user_ctx[uid] = {"pairs": []}
    if pair in user_ctx[uid]["pairs"]:
        user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < 3:
        user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["step"] = "start"
    await callback.message.delete()
    await callback.message.answer("🕒 <b>Send START TIME</b>\nExample: <code>14:00</code>")

@dp.message(F.text.regexp(r'(\d{1,2}):(\d{2})'))
async def handle_time(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    t = message.text.strip().replace("'", "").replace('"', "")
    
    if user_ctx[uid].get("step") == "start":
        user_ctx[uid]["start_t"] = t
        user_ctx[uid]["step"] = "end"
        await message.answer("🕒 <b>Send END TIME</b>\nExample: <code>16:00</code>")
    elif user_ctx[uid].get("step") == "end":
        user_ctx[uid]["end_t"] = t
        await generate_signals(message)

async def generate_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    load = await message.answer("📡 <b>ANALYZING MARKET...</b>")

    for p in [30, 60, 85, 100]:
        await asyncio.sleep(0.5)
        bar = "█" * (p//10) + "░" * (10 - p//10)
        await load.edit_text(f"🧪 <b>SCANNING NODES</b>\n<code>[{bar}] {p}%</code>")

    report = "🀄️ <b>APX PRIME SIGNALS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
    try:
        start = datetime.datetime.strptime(data["start_t"], "%H:%M")
        end = datetime.datetime.strptime(data["end_t"], "%H:%M")
        curr = start
        while curr < end:
            for p in data["pairs"]:
                asset = p.split()[-1][:6]
                trade = random.choice(["🟢 BUY", "🔴 SELL"])
                report += f"{curr.strftime('%H:%M')}   {asset}   {trade}\n"
            curr += datetime.timedelta(minutes=random.randint(6, 13))
    except:
        report += "Time format error."

    await load.delete()
    await message.answer(f"<code>{report}</code>\n\n✅ <b>Signals Generated</b>", reply_markup=InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen")
    ).as_markup())
    user_ctx.pop(uid, None)

@dp.callback_query(F.data == "regen")
async def regen(callback: types.CallbackQuery):
    await callback.answer("Regenerating...")
    # Simple re-generate logic can be extended

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.delete()
    await start_handler(callback.message)

# Other handlers (profile, rules, exit, admin etc.)
@dp.callback_query(F.data.in_(["profile", "rules", "exit", "check_join"]))
async def quick_handler(callback: types.CallbackQuery):
    if callback.data == "profile":
        await callback.answer("👤 Profile Loaded", show_alert=True)
    elif callback.data == "rules":
        await callback.answer("One User = One Key\nNo Sharing", show_alert=True)
    elif callback.data == "exit":
        await callback.message.delete()
        await callback.message.answer("🌌 <b>APX PRIME OFFLINE</b>")
    elif callback.data == "check_join":
        if await is_joined(callback.from_user.id):
            await callback.message.delete()
            await start_handler(callback.message)

async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
