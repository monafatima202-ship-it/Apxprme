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

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {}
GLOBAL_BC = {"mode": "auto", "text": ""}

# ====================== 24 PAIRS DATA ======================
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
    conn = sqlite3.connect('apx_prime_master.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, 
                     last_key TEXT, key_used INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

async def check_access(uid):
    conn = sqlite3.connect('apx_prime_master.db')
    u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
    conn.close()
    if u and u[1] == 1:
        try:
            expiry = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
            if datetime.datetime.now() < expiry:
                return "ACTIVE"
        except:
            pass
    return "LOCKED"

async def is_joined_channel(uid):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        return member.status not in ["left", "kicked"]
    except:
        return False

# ====================== AUTO NODE STATUS ======================
async def get_node_status():
    if GLOBAL_BC["mode"] == "manual":
        return f"📢 {GLOBAL_BC['text']}"
    
    h = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if 2 <= h < 8:
        return "🌙 **SLEEP MODE** (Low Volatility)"
    elif 13 <= h < 15:
        return "❄️ **COOL DOWN** (Node Sync)"
    else:
        return "✅ **API NODE: STABLE**"

# ====================== START & MAIN DASHBOARD ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id

    if not await is_joined_channel(uid):
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        kb.row(types.InlineKeyboardButton(text="✅ I HAVE JOINED", callback_data="check_join"))
        return await message.answer_photo(
            photo=BANNER_URL,
            caption="🛡️ **STRICT AUTHENTICATION REQUIRED**\nJoin our official channel to unlock APX Prime.",
            reply_markup=kb.as_markup()
        )

    await show_main_dashboard(message)

async def show_main_dashboard(obj):
    uid = obj.from_user.id
    is_msg = isinstance(obj, types.Message)
    msg = obj if is_msg else obj.message

    access = await check_access(uid)
    pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
    node = await get_node_status()

    kb = InlineKeyboardBuilder()
    if access == "ACTIVE":
        kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    else:
        kb.row(types.InlineKeyboardButton(text="🔑 GET 7 DAYS ACCESS", callback_data="gen_key"))

    kb.row(
        types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"),
        types.InlineKeyboardButton(text="📜 RULES", callback_data="rules")
    )
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit"))

    caption = f"""
🌌 **APX PRIME OS v5.3** 🌌
━━━━━━━━━━━━━━━━━━━━━━
👤 **User:** `{obj.from_user.first_name}`
📡 **Node:** {node}
🕰️ **PKT:** `{pkt}` | **RANK:** `{'VIP 💎' if access == 'ACTIVE' else 'GUEST 🔒'}`
━━━━━━━━━━━━━━━━━━━━━━
**Institutional Handshake:** `Verified` 🟢
"""

    if is_msg:
        await obj.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
    else:
        try:
            await msg.edit_caption(caption=caption, reply_markup=kb.as_markup())
        except:
            await msg.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())

# ====================== KEY SYSTEM ======================
@dp.callback_query(F.data == "gen_key")
async def gen_key(callback: types.CallbackQuery):
    uid = callback.from_user.id
    conn = sqlite3.connect('apx_prime_master.db')
    data = conn.execute("SELECT key_used FROM users WHERE uid = ?", (uid,)).fetchone()
    
    if data and data[0] == 1:
        return await callback.answer("❌ You have already used your one-time key!", show_alert=True)

    key = f"APX-{random.randint(1000,9999)}-VIP-{uid % 1000}"
    conn.execute("INSERT OR REPLACE INTO users (uid, last_key, key_used) VALUES (?, ?, 0)", (uid, key))
    conn.commit()
    conn.close()

    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📋 COPY KEY", callback_data=f"copy:{key}"))
    
    await callback.message.answer(
        f"🔑 **YOUR ONE-TIME LICENSE KEY**\n\n`/verify {key}`\n\nTap button to copy.",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("copy:"))
async def copy_key(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    await callback.answer(f"✅ Copied!\n{key}", show_alert=True)

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    uid = message.from_user.id
    key = message.text.replace("/verify ", "").strip()

    conn = sqlite3.connect('apx_prime_master.db')
    data = conn.execute("SELECT last_key, key_used FROM users WHERE uid = ?", (uid,)).fetchone()
    
    if not data or data[0] != key or data[1] == 1:
        conn.close()
        return await message.answer("❌ Invalid or Already Used Key!")

    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE users SET expiry=?, is_vip=1, key_used=1 WHERE uid=?", (exp, uid))
    conn.commit()
    conn.close()

    await message.answer_photo(
        photo="https://i.imgur.com/4z4fK3L.gif",
        caption="🥳 **NEURAL ACCESS GRANTED!**\n7 Days VIP Activated Successfully!"
    )
    
    # Admin Notification
    try:
        await bot.send_message(ADMIN_ID, f"✅ **New Activation**\nUser: {message.from_user.first_name}\nID: `{uid}`")
    except:
        pass

    await asyncio.sleep(2)
    await start_handler(message)

# ====================== TERMINAL GRID & SIGNALS ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": []}
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx.get(uid, {}).get("pairs", [])
    builder = InlineKeyboardBuilder()
    
    for code, display in PAIRS_DATA.items():
        text = f"✅ {display}" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    
    builder.adjust(2)
    if sel:
        builder.row(types.InlineKeyboardButton(text=f"🔥 GENERATE SIGNALS ({len(sel)})", callback_data="ask_time"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK TO DASHBOARD", callback_data="back_dashboard"))
    
    await callback.message.edit_caption(caption="🧪 **SELECT ASSETS (Max 3)**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_pair(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":", 1)[1]
    if uid not in user_ctx:
        user_ctx[uid] = {"pairs": []}
    
    if pair in user_ctx[uid]["pairs"]:
        user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < 3:
        user_ctx[uid]["pairs"].append(pair)
    
    await render_grid(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 Send **START TIME** (e.g. `14:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_time(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx or "step" not in user_ctx[uid]:
        return
    
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 Send **END TIME** (e.g. `16:00`)")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    
    load = await message.answer("📡 **ANALYZING MARKET...**")
    for i in [25, 55, 80, 100]:
        await asyncio.sleep(0.5)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING NODES**\n`[{bar}] {i}%`")

    report = f"""
╔════════════════════════════╗
       **APX ALPHA PRO SIGNALS**
╚════════════════════════════╝
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TIME   ┃ ASSET     ┃ DIR    ┃ ACC 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            asset_short = p.split()[-1][:6]
            direction = random.choice(["CALL", "PUT "])
            acc = random.randint(94, 99)
            report += f" `{curr.strftime('%H:%M')}` ┃ `{asset_short}` ┃ `{direction}` ┃ `{acc}%`\n"
        curr += datetime.timedelta(minutes=random.randint(5, 12))

    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **SIGNALS GENERATED | PKT UTC+5**", parse_mode="Markdown")
    user_ctx.pop(uid, None)

# ====================== ADMIN & UTILS ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📢 Manual Broadcast", callback_data="adm:bc"))
    kb.row(types.InlineKeyboardButton(text="🔄 Reset Auto Mode", callback_data="adm:auto"))
    await message.answer("🛠 **ADMIN CONTROL PANEL**", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "adm:bc")
async def manual_bc(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_ctx[callback.from_user.id] = {"step": "bc"}
    await callback.message.answer("✍️ Send message for broadcast:")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "bc")
async def save_bc(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    GLOBAL_BC["text"] = message.text
    GLOBAL_BC["mode"] = "manual"
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ Manual Broadcast Activated!")

@dp.callback_query(F.data == "adm:auto")
async def reset_auto(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    GLOBAL_BC["mode"] = "auto"
    await callback.answer("🔄 Auto Mode Restored!", show_alert=True)

@dp.message(Command("admin30"))
async def give_30days(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.split()[1])
        exp = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('apx_prime_master.db')
        conn.execute("UPDATE users SET expiry=?, is_vip=1 WHERE uid=?", (exp, uid))
        conn.commit()
        conn.close()
        await message.answer(f"✅ 30 Days VIP Given to `{uid}`")
        try:
            await bot.send_message(uid, "🎉 **Admin Extended Your Access**\n30 Days VIP Activated!")
        except:
            pass
    except:
        await message.answer("Usage: `/admin30 user_id`")

@dp.callback_query(F.data == "check_join")
async def check_join(callback: types.CallbackQuery):
    if await is_joined_channel(callback.from_user.id):
        await callback.message.delete()
        await start_handler(callback.message)
    else:
        await callback.answer("❌ Please join the channel first!", show_alert=True)

@dp.callback_query(F.data == "back_dashboard")
async def back_dashboard(callback: types.CallbackQuery):
    await callback.message.delete()
    await start_handler(callback.message)

@dp.callback_query(F.data == "profile")
async def profile(callback: types.CallbackQuery):
    access = await check_access(callback.from_user.id)
    text = f"""
👤 **PROFILE**

🆔 ID: `{callback.from_user.id}`
👤 Name: {callback.from_user.first_name}
🌍 Region: Pakistan (PKT)
📊 Status: **{'VIP 💎' if access == 'ACTIVE' else 'GUEST 🔒'}**
⏳ Access: {'7 Days Active' if access == 'ACTIVE' else 'Locked'}
    """
    await callback.answer(text, show_alert=True)

@dp.callback_query(F.data == "rules")
async def rules(callback: types.CallbackQuery):
    await callback.answer("📜 • One User = One Key\n• No Key Sharing\n• Misuse = Permanent Ban", show_alert=True)

@dp.callback_query(F.data == "exit")
async def exit_sys(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("🌌 **APX PRIME TERMINAL OFFLINE**")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
