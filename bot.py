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

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, temp_key TEXT)''')
    conn.commit()
    conn.close()

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
            kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))
            await bot.send_photo(uid, BANNER_URL, 
                caption=f"<b>🌌 APX PRIME OS v190.0</b>\n\nHello <b>{callback.from_user.first_name}</b>! 👋",
                reply_markup=kb.as_markup())
        else:
            await callback.answer("❌ Join channel first!", show_alert=True)
    except:
        await callback.answer("⚠️ Error", show_alert=True)

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
    
    await callback.message.answer(f"🔑 <b>7-DAY ACCESS KEY</b>\n\n<code>{key}</code>\n\nSend: <code>/verify {key}</code>")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    try:
        key = message.text.split(maxsplit=1)[1].strip()
    except:
        return await message.answer("❌ Use: <code>/verify YOUR_KEY</code>")

    conn = sqlite3.connect('apx_stable_v190.db')
    row = conn.execute("SELECT temp_key FROM users WHERE uid = ?", (message.from_user.id,)).fetchone()
    conn.close()

    if not row or row[0] != key:
        return await message.answer("❌ <b>Invalid Key!</b>")

    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit()
    conn.close()

    await message.answer(f"✅ <b>7 DAYS ACCESS ACTIVATED!</b>\nValid until: <code>{exp[:10]}</code>")
    await show_mode_selection(message)

# ====================== MODE & PAIR SELECTION (FREEZE FIXED) ======================
async def show_mode_selection_msg(uid: int):
    user_ctx[uid] = {"pairs": [], "last_report": None, "strategy": None, "mode": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await bot.send_message(uid, "⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb.as_markup())

async def show_mode_selection(message: types.Message):
    await show_mode_selection_msg(message.from_user.id)

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    await callback.answer("✅ Mode Selected!")
    uid = callback.from_user.id
    user_ctx.setdefault(uid, {"pairs": [], "last_report": None, "strategy": None})
    user_ctx[uid]["mode"] = callback.data.split(":")[1]
    await send_pair_selection(uid)   # New function to avoid edit issues

async def send_pair_selection(uid: int):
    """Sends fresh message for pair selection to prevent freezing"""
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
        "🧪 <b>SELECT ASSETS (MAX 3):</b>\n<i>Tap to select / deselect</i>",
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
    await callback.message.delete()   # Delete old grid
    await send_pair_selection(uid)    # Send fresh updated grid

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
    await callback.message.edit_caption("📈 <b>SELECT YOUR AI STRATEGY:</b>", reply_markup=kb.as_markup())

# ====================== STRATEGY + TIME + SIGNALS ======================
@dp.callback_query(F.data.startswith("strat:"))
async def set_strategy(callback: types.CallbackQuery):
    uid = callback.from_user.id
    user_ctx[uid]["strategy"] = STRATEGIES[callback.data.split(":")[1]]
    user_ctx[uid]["step"] = "start_t"
    await callback.message.delete()
    await bot.send_message(uid, "🕒 <b>Enter Start Time</b> (e.g. <code>16:00</code>)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or "step" not in data: return

    if data["step"] == "start_t":
        data["start_t"] = message.text
        data["step"] = "end_t"
        await message.answer("🕒 <b>Enter End Time</b> (e.g. <code>18:00</code>)")
    elif data["step"] == "end_t":
        data["end_t"] = message.text
        await execute_live_signals(message)

# ====================== COLORFUL LOADING + CLEAN SIGNALS ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or not data.get("pairs"):
        return await bot.send_message(uid, "⚠️ Please select assets first.")

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        load = await bot.send_message(uid, "🌌 <b>APX PRIME OS ACTIVATING</b>\n<code>░░░░░░░░░░ 0%</code> ✨")
        stages = [("40%", "▓▓▓░░░░░░"), ("75%", "▓▓▓▓▓▓░░░░"), ("98%", "▓▓▓▓▓▓▓▓▓░")]
        for p, bar in stages:
            await asyncio.sleep(0.45)
            await load.edit_text(f"🌌 <b>APX PRIME OS ACTIVATING</b>\n<code>{bar} {p}</code> ⚡")

        signals = []
        async with aiohttp.ClientSession() as session:
            for pair in data["pairs"]:
                try:
                    async with session.get(f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100", timeout=15) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.splitlines():
                                if "=>" in line:
                                    parts = [p.strip() for p in line.split("=>")]
                                    if len(parts) >= 3:
                                        t_str = parts[1]
                                        direction = parts[2].strip().upper()
                                        try:
                                            sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                                            start_t = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
                                            end_t = datetime.datetime.strptime(data['end_t'], "%H:%M").time()
                                            if start_t <= sig_time <= end_t:
                                                signals.append((sig_time, pair, direction, t_str))
                                        except: pass
                except: pass

        signals.sort(key=lambda x: x[0])

        body = ""
        for _, pair, direction, t in signals:
            arrow = "↑" if direction == "CALL" else "↓"
            body += f"⧉ <b>{t}</b> • {pair} {arrow} <b>{direction}</b>\n"

        if not body:
            body = "⚠️ No signals found in selected time range.\n"

        report_content = (
            f"<b>🌍 APX PRIME OS v190.0</b>\n"
            f"⏰ <b>{data['start_t']} - {data['end_t']}</b> (UTC+6)\n"
            f"📊 Strategy: <b>{data['strategy']}</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            f"{body}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"❗ <i>High Accuracy • 1% Risk Only</i>"
        )
        
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen_sig"))
    kb.row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_signals"))
    kb.row(types.InlineKeyboardButton(text="🔄 CHANGE PAIRS", callback_data="change_pair_back"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    await bot.send_message(uid, f"<b>📡 LIVE SIGNALS GENERATED</b>\n\n<code>{report_content}</code>", reply_markup=kb.as_markup())

# ====================== OTHER CALLBACKS ======================
@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("🔄 Refreshing...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Copied to clipboard!", show_alert=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, f"<code>APX PRIME TERMINAL CLOSED\nGoodbye {callback.from_user.first_name} 👋</code>")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
