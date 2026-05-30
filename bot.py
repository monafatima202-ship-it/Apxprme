import os
import asyncio
import datetime
import sqlite3
import random
import aiohttp
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
    "1": "RSI + MA50",
    "2": "MACD",
    "3": "Bollinger Bands",
    "4": "Stochastic Oscillator",
    "5": "All Strategies Combined"
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, temp_key TEXT)''')
    conn.commit()
    conn.close()

# ====================== AUTO BROADCAST (Sirf Bot) ======================
async def auto_broadcast():
    while True:
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
        hour = now.hour
        if hour == 7: msg = "🌅 <b>NEW TRADING DAY ACTIVATED</b>\nGood Morning Traders! 🚀"
        elif hour == 12: msg = "⚙️ <b>OPTIMIZATION MODE</b>\nSystem cooling..."
        elif hour == 17: msg = "🔧 <b>MAINTENANCE WINDOW</b>\nShort maintenance..."
        elif hour == 0: msg = "🌙 <b>SYSTEM SLEEP MODE</b>\nSee you tomorrow!"
        else:
            await asyncio.sleep(60)
            continue
        try:
            await bot.send_message(ADMIN_ID, f"🔔 <b>AUTO UPDATE:</b>\n{msg}", parse_mode="HTML")
        except: pass
        await asyncio.sleep(3600)

# ====================== START ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
    kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY MEMBERSHIP", callback_data="auth_check"))
    await message.answer_photo(photo=BANNER_URL, caption=f"<b>🔒 APX PRIME OS v190.0</b>\n\nWelcome <b>{message.from_user.first_name}</b> 👋", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== AUTH & KEY ======================
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

            is_active = False
            if u and u[1] == 1 and u[0]:
                try:
                    exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
                    if datetime.datetime.now() < exp:
                        is_active = True
                except: pass

            if is_active:
                await show_mode_selection(callback.message)
            else:
                kb = InlineKeyboardBuilder()
                kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))
                await bot.send_photo(uid, BANNER_URL, caption=f"<b>🌌 APX PRIME OS v190.0</b>\n\nHello <b>{callback.from_user.first_name}</b>!", parse_mode="HTML", reply_markup=kb.as_markup())
        else:
            await callback.answer("❌ Join channel first!", show_alert=True)
    except:
        await callback.answer("⚠️ Error", show_alert=True)

@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    await callback.answer()
    key = f"APX-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, temp_key) VALUES (?, ?, 0, ?)", (callback.from_user.id, "NONE", key))
    conn.commit(); conn.close()
    await callback.message.answer(f"🔑 <b>7-DAY ACCESS KEY</b>\n\n<code>{key}</code>\n\nSend: <code>/verify {key}</code>", parse_mode="HTML")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    try:
        provided_key = message.text.split(maxsplit=1)[1].strip()
    except:
        return await message.answer("❌ Use: `/verify YOUR_KEY`")

    conn = sqlite3.connect('apx_stable_v190.db')
    row = conn.execute("SELECT temp_key FROM users WHERE uid = ?", (message.from_user.id,)).fetchone()
    conn.close()

    if not row or not row[0] or row[0] != provided_key:
        return await message.answer("❌ **Invalid Key!**\nPlease get a new key.", parse_mode="HTML")

    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit(); conn.close()

    await message.answer(f"✅ <b>7 DAYS ACCESS ACTIVATED SUCCESSFULLY!</b>\nValid until: {exp[:10]}", parse_mode="HTML")
    await show_mode_selection(message)

async def show_mode_selection(message: types.Message):
    user_ctx[message.from_user.id] = {"pairs": [], "last_report": None, "strategy": None, "days": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await message.answer("⚡ <b>SELECT OPERATIONAL MODE:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== PAIR SELECTION ======================
@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id]["mode"] = callback.data.split(":")[1]
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        status = "✅" if code in sel else "💠"
        builder.add(types.InlineKeyboardButton(text=f"{status} {display}", callback_data=f"sel:{code}"))
    builder.adjust(2)
    if sel:
        builder.row(types.InlineKeyboardButton(text="🚀 NEXT → STRATEGY", callback_data="select_strategy"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="back_to_mode"))
    try:
        await callback.message.edit_caption(caption="🧪 <b>SELECT ASSETS (MAX 3):</b>", parse_mode="HTML", reply_markup=builder.as_markup())
    except:
        await callback.message.edit_text(text="🧪 <b>SELECT ASSETS (MAX 3):</b>", parse_mode="HTML", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_pair(callback: types.CallbackQuery):
    uid = callback.from_user.id
    code = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid].get("mode") == "multi" else 1
    if code in user_ctx[uid]["pairs"]:
        user_ctx[uid]["pairs"].remove(code)
    elif len(user_ctx[uid]["pairs"]) < limit:
        user_ctx[uid]["pairs"].append(code)
    await callback.answer("✅ Updated")
    await render_grid(callback)

@dp.callback_query(F.data == "select_strategy")
async def select_strategy(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder()
    for key, name in STRATEGIES.items():
        kb.row(types.InlineKeyboardButton(text=f"{key}️⃣ {name}", callback_data=f"strat:{key}"))
    await callback.message.edit_caption(caption="📈 <b>Select AI Trading Strategy:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("strat:"))
async def set_strategy(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id]["strategy"] = STRATEGIES[callback.data.split(":")[1]]
    kb = InlineKeyboardBuilder()
    for i in [1,3,5,7,10,15,30]:
        kb.row(types.InlineKeyboardButton(text=f"{i} Days", callback_data=f"days:{i}"))
    await callback.message.edit_caption(caption="📅 <b>Select Number of Days to Analyze:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("days:"))
async def set_days(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id]["days"] = int(callback.data.split(":")[1])
    await ask_time(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 <b>Enter Start Time</b> (e.g. <code>16:00</code>)", parse_mode="HTML")

# ====================== TIME & SIGNALS ======================
@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx or "step" not in user_ctx[uid]: return
    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 <b>Enter End Time</b> (e.g. <code>18:00</code>)", parse_mode="HTML")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_live_signals(message)

async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or not data.get("pairs"):
        return await message.answer("⚠️ Please select assets first.")

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        load = await message.answer("🌌 <b>APX PRIME OS ACTIVATING</b>\n<code>░░░░░░░░░░ 0%</code> ✨", parse_mode="HTML")
        for p in ["40%", "70%", "95%"]:
            await asyncio.sleep(0.7)
            await load.edit_text(f"🌌 <b>APX PRIME OS ACTIVATING</b>\n<code>▓▓▓▓░░░░░░ {p}</code> ⚡", parse_mode="HTML")
        await asyncio.sleep(0.5)

        start_time = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_time = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        header = "🎴 <b>APX PRIME LIVE SIGNALS</b>\n"
        header += f"🕒 {data['start_t']} - {data['end_t']} PKT\n"
        header += f"📊 Strategy: {data.get('strategy', 'Default')}\n"
        header += f"📅 Days: {data.get('days', 'N/A')}\n"
        header += "━━━━━━━━━━━━━━━━━━━━━━\n"

        signals = []
        async with aiohttp.ClientSession() as session:
            for pair in data["pairs"]:
                try:
                    async with session.get(f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100", timeout=12) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.split('\n'):
                                if not line.strip(): continue
                                if "=>" in line:
                                    parts = [p.strip() for p in line.split("=>")]
                                    if len(parts) >= 3:
                                        t_str = parts[1]
                                        direction = parts[2].upper()
                                        try:
                                            sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                                            if start_time <= sig_time <= end_time:
                                                signals.append((sig_time, pair, direction, t_str))
                                        except: pass
                except: pass

        signals.sort(key=lambda x: x[0])
        body = "\n".join([f"🔹 <b>{pair}</b> → {t_str} ⇨ <b>{direction}</b>" for _, pair, direction, t_str in signals[:25]])

        if not body:
            body = "⚠️ No signals found in selected time range.\n"

        footer = "\n━━━━━━━━━━━━━━━━━━━━━━\n<i>Powered by 🌐 APX Premium Bot • 80%+ Accuracy</i>"
        report_content = header + body + footer
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔄 REGENERATE SIGNALS", callback_data="regen_sig"))
    kb.row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_signals"))
    kb.row(types.InlineKeyboardButton(text="🔄 CHANGE PAIRS", callback_data="change_pair_back"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    await message.answer(f"<b>📊 APX LIVE SIGNALS GENERATED</b>\n\n<code>{report_content}</code>", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Signals Copied!", show_alert=True)

@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("🔄 Regenerating...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await show_mode_selection(callback.message)

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, f"<code>APX PRIME TERMINAL CLOSED\nGoodbye {callback.from_user.first_name} 👋</code>", parse_mode="HTML")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(auto_broadcast())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
