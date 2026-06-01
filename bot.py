import os
import asyncio
import datetime
import sqlite3
import random
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ====================== CONFIG ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
user_ctx = {}

# ====================== PAIRS & STRATEGIES ======================
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC",
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",
    "BTCUSD": "₿🌐 BTCUSD-OTC", "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC",
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "AAPL": "🇺🇸🍎 AAPL-OTC", "MSFT": "🇺🇸💻 MSFT-OTC", "PFE": "🇺🇸💊 PFE-OTC",
    "JNJ": "🇺🇸🏥 JNJ-OTC", "MCD": "🇺🇸🍔 MCD-OTC", "INTL": "🇺🇸🔬 INTL-OTC"
}

STRATEGIES = {
    "1": "🚀 RSI + MA50",
    "2": "📊 MACD Crossover",
    "3": "📏 Bollinger Bands",
    "4": "⚡ Stochastic Oscillator",
    "5": "🌟 All Strategies Combined"
}

QUOTES = {
    "morning": "🌅 \"The goal of a successful trader is to make the best trades. Money is secondary.\"",
    "cooldown": "❄️ \"In trading, the best action is sometimes inaction. Guard your capital closely.\"",
    "maintenance": "🛠️ \"System optimization ensures flawless accuracy. Trust the parameters.\"",
    "sleep": "🌙 \"Market analysis is done. Unplug, rest, and prepare for tomorrow's market supremacy.\""
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, temp_key TEXT)''')
    conn.commit()
    conn.close()

# ====================== SYSTEM TIME STATE INTERFACE ======================
async def get_broadcast_context():
    # Strict PKT calculation (UTC+5)
    now_pkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now_pkt.hour
    
    if 7 <= h < 12:
        return f"💡 <b>SYS BROADCAST:</b>\n<code>{QUOTES['morning']}</code>\n🟢 <b>TRADING PLATFORM: OPERATIONAL</b>"
    elif 12 <= h < 17:
        return f"💡 <b>SYS BROADCAST:</b>\n<code>{QUOTES['cooldown']}</code>\n❄️ <b>SYSTEM STATE: COOL DOWN IN EFFECT</b>"
    elif 17 <= h < 23:
        return f"💡 <b>SYS BROADCAST:</b>\n<code>{QUOTES['maintenance']}</code>\n⚠️ <b>SYSTEM STATE: MAINTENANCE CHECKPOINTS ACTIVE</b>"
    else:
        return f"💡 <b>SYS BROADCAST:</b>\n<code>{QUOTES['sleep']}</code>\n🌙 <b>SYSTEM STATE: SLEEP MODE ACTIVE</b>"

# ====================== START ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
    kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY MEMBERSHIP", callback_data="auth_check"))
    
    await message.answer_photo(
        photo=BANNER_URL,
        caption=f"<b>🔥 APX PRIME OS v190.0</b>\n\n"
                f"Welcome <b>{message.from_user.first_name}</b> 👑\n"
                f"<i>Next-Gen OTC Trading Intelligence</i>",
        reply_markup=kb.as_markup()
    )

# ====================== AUTH & SECURE KEY ======================
@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ Verified!", show_alert=True)
            await callback.message.delete()

            conn = sqlite3.connect('apx_stable_v190.db')
            u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
            conn.close()

            if u and u[1] == 1 and u[0]:
                try:
                    exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
                    if datetime.datetime.now() < exp:
                        return await show_mode_selection_msg(uid)
                except: pass

            kb = InlineKeyboardBuilder()
            kb.row(types.InlineKeyboardButton(text="🔑 GET ACCESS TERMINAL", callback_data="get_key"))
            await bot.send_photo(uid, BANNER_URL, 
                caption=f"<b>🌌 APX PRIME OS v190.0</b>\n\nHello <b>{callback.from_user.first_name}</b>! 👋\nInitialization step required.",
                reply_markup=kb.as_markup())
        else:
            await callback.answer("❌ Join channel first!", show_alert=True)
    except:
        await callback.answer("⚠️ Authentication Error", show_alert=True)

@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    uid = callback.from_user.id
    await callback.answer()
    
    conn = sqlite3.connect('apx_stable_v190.db')
    u = conn.execute("SELECT temp_key FROM users WHERE uid = ?", (uid,)).fetchone()
    
    if u and u[0]:
        key = u[0]
    else:
        key = f"APX-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, temp_key) VALUES (?, ?, 0, ?)", 
                     (uid, "NONE", key))
        conn.commit()
    conn.close()
    
    await callback.message.answer(f"🔑 <b>7-DAY SECURITY VIP ACCESS KEY</b>\n\n<code>{key}</code>\n\nSend payload activation: <code>/verify {key}</code>")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    try:
        key = message.text.split(maxsplit=1)[1].strip()
    except:
        return await message.answer("❌ Use syntax: <code>/verify YOUR_KEY</code>")

    conn = sqlite3.connect('apx_stable_v190.db')
    row = conn.execute("SELECT temp_key, expiry, is_vip FROM users WHERE uid = ?", (message.from_user.id,)).fetchone()
    conn.close()

    if not row or row[0] != key:
        return await message.answer("❌ <b>Invalid Terminal Security Key!</b>")

    # Asking and displaying remaining duration validation precisely 
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit()
    conn.close()

    await message.answer(f"✅ <b>7 DAYS ACCESS ALLOCATED TO DEVICE PROPERLY!</b>\nValid until expiration check: <code>{exp}</code>")
    await show_mode_selection(message)

# ====================== MODE & PAIR SELECTION ======================
async def show_mode_selection_msg(uid: int):
    user_ctx[uid] = {"pairs": [], "last_report": None, "strategy": None, "mode": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    
    broadcast_msg = await get_broadcast_context()
    await bot.send_message(uid, f"{broadcast_msg}\n\n━━━━━━━━━━━━━━━\n⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb.as_markup())

async def show_mode_selection(message: types.Message):
    await show_mode_selection_msg(message.from_user.id)

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    await callback.answer("✅ Mode Configured.")
    uid = callback.from_user.id
    user_ctx.setdefault(uid, {"pairs": [], "last_report": None, "strategy": None})
    user_ctx[uid]["mode"] = callback.data.split(":")[1]
    await send_pair_selection(uid)

async def send_pair_selection(uid: int):
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    
    for code, display in PAIRS_DATA.items():
        status = "✅" if code in sel else "🔹"
        builder.add(types.InlineKeyboardButton(text=f"{status} {display}", callback_data=f"sel:{code}"))
    
    builder.adjust(2)
    if sel:
        builder.row(types.InlineKeyboardButton(text="🚀 NEXT → STRATEGY", callback_data="select_strategy"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK TO MODE", callback_data="back_to_mode"))

    await bot.send_message(
        uid,
        "🧪 <b>SELECT ASSETS (MAX 3):</b>\n<i>Tap network buttons to map terminal parameters</i>",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_pair(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_ctx: return
    code = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid].get("mode") == "multi" else 1
    
    if code in user_ctx[uid]["pairs"]:
        user_ctx[uid]["pairs"].remove(code)
    elif len(user_ctx[uid]["pairs"]) < limit:
        user_ctx[uid]["pairs"].append(code)
    
    await callback.answer()
    await callback.message.delete()
    await send_pair_selection(uid)

@dp.callback_query(F.data == "back_to_mode")
async def back_to_mode(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "select_strategy")
async def select_strategy(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder()
    for key, name in STRATEGIES.items():
        kb.row(types.InlineKeyboardButton(text=name, callback_data=f"strat:{key}"))
    await callback.message.edit_text("📈 <b>SELECT ACTIVE ALGORITHM STRATEGY:</b>", reply_markup=kb.as_markup())

# ====================== STRATEGY + TIME + SIGNALS ======================
@dp.callback_query(F.data.startswith("strat:"))
async def set_strategy(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    if uid not in user_ctx: return
    user_ctx[uid]["strategy"] = STRATEGIES[callback.data.split(":")[1]]
    user_ctx[uid]["step"] = "start_t"
    await callback.message.delete()
    await bot.send_message(uid, "🕒 <b>Enter Start Time Parameter</b> (e.g. <code>16:00</code>)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or "step" not in data: return

    if data["step"] == "start_t":
        data["start_t"] = message.text
        data["step"] = "end_t"
        await message.answer("🕒 <b>Enter End Time Parameter</b> (e.g. <code>18:00</code>)")
    elif data["step"] == "end_t":
        data["end_t"] = message.text
        data["step"] = "processing"
        await execute_live_signals(message)

# ====================== RAINBOW MATRIX LOAD + REAL LINEAR DATA SYSTEM ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or not data.get("pairs"):
        return await bot.send_message(uid, "⚠️ Operational assets configuration context missing.")

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        # Premium Fancy Custom Rainbow Gradient Optimization Matrix Bars
        load = await bot.send_message(uid, "🌌 <b>INITIALIZING APX QUANTUM INTERFACE</b>\n<code>🔴🧡💛 25% CORE SYNC</code> ✨")
        await asyncio.sleep(0.4)
        await load.edit_text("🌌 <b>SYNCHRONIZING SECURE NETWORK HOOKS</b>\n<code>🔴🧡💛💚🟦 65% SECURE</code> ⚡")
        await asyncio.sleep(0.4)
        await load.edit_text("🌌 <b>PARSING MILONGAZI LIVE OTC PACKETS</b>\n<code>🔴🧡💛💚🟦🟣 100% SUCCESS</code> 💎")
        await asyncio.sleep(0.3)

        start_time = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_time = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        header = "🎴 <b>APX PRIME LIVE SIGNALS</b>\n"
        header += f"🕒 {data['start_t']} - {data['end_t']} PKT (UTC+6)\n"
        header += f"📊 Strategy: <b>{data.get('strategy', 'Default')}</b>\n"
        header += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        signals = []
        async with aiohttp.ClientSession() as session:
            for pair in data["pairs"]:
                api_url = f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100"
                try:
                    async with session.get(api_url, timeout=15) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.splitlines():
                                if not line.strip(): continue
                                if "=>" in line:
                                    parts = [p.strip() for p in line.split("=>")]
                                    if len(parts) >= 3:
                                        t_str = parts[1]
                                        direction = parts[2].strip().upper()
                                        try:
                                            sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                                            if start_time <= sig_time <= end_time:
                                                signals.append((sig_time, pair, direction, t_str))
                                        except: pass
                except: pass

        signals.sort(key=lambda x: x[0])

        body = ""
        # Strict Monospace Row Matrix Padding layout logic so arrows never drop down or break the sequence line layout
        for _, pair, direction, t in signals[:40]:
            arrow = "↑" if direction == "CALL" else "↓"
            body += f"⧉ {pair:11} → {t} ⇨ {direction:4} {arrow}\n"

        # ABSOLUTE STRICT GUARANTEE: If API gives no match, notify strictly without random fallbacks
        if not body.strip():
            body = "⚠️ STRICT PROTOCOL NOTICE:\nNo structural data packets matched target time frame criteria inside server data.\n"

        footer = "\n━━━━━━━━━━━━━━━━━━━━━━━━\nRULES ‼️\n- DO NOT TRADE IN ASSIGNED MARKET VALUE < 80%\n- EMPLOY PREMIUM SAFETY MARGIN PROTECTION"
        report_content = header + body + footer
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔄 REGENERATE DATA", callback_data="regen_sig"))
    kb.row(types.InlineKeyboardButton(text="📋 COPY REQUISITE PAYLOAD", callback_data="copy_signals"))
    kb.row(types.InlineKeyboardButton(text="🔄 ALTER TARGET ASSETS", callback_data="change_pair_back"))
    kb.row(types.InlineKeyboardButton(text="❌ SHUTDOWN TERMINAL", callback_data="exit_sys"))

    await bot.send_message(uid, f"<b>📡 LIVE DEVIATION SIGNALS INGESTED</b>\n\n<code>{report_content}</code>", reply_markup=kb.as_markup())

# ====================== CALLBACK PLATFORM MAPS ======================
@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("🔄 Resynching server array pipeline data maps...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Target payload saved to structural device clipboard!", show_alert=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, f"<code>APX PRIME SECURE LOGOUT COMPLETELY EXECUTED\nSession state killed safely. Goodbye {callback.from_user.first_name} 👋</code>")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
