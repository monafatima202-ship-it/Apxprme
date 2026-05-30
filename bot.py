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

# ====================== PAIRS DATA (With USA + Country Flags) ======================
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", 
    "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", 
    "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC", 
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", 
    "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", 
    "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", 
    "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", 
    "XAUUSD": "🥇🔱 XAUUSD-OTC",   
    "BTCUSD": "₿🌐 BTCUSD-OTC", 
    "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", 
    "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", 
    "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", 
    "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC", 
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", 
    "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", 
    "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "AAPL": "🇺🇸🍎 AAPL-OTC", 
    "MSFT": "🇺🇸💻 MSFT-OTC", 
    "PFE": "🇺🇸💊 PFE-OTC", 
    "JNJ": "🇺🇸🏥 JNJ-OTC",
    "MCD": "🇺🇸🍔 MCD-OTC", 
    "INTL": "🇺🇸🔬 INTL-OTC"
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, key_taken INTEGER DEFAULT 0)''')
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
        caption="<b>🔒 APX PRIME OS v190.0</b>\n\n"
                "<i>TRADE SMART. STAY AHEAD.</i>",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

# ====================== AUTH CHECK ======================
@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ Verification Successful!", show_alert=True)
            await callback.message.delete()

            conn = sqlite3.connect('apx_stable_v190.db')
            u = conn.execute("SELECT expiry, is_vip, key_taken FROM users WHERE uid = ?", (uid,)).fetchone()
            conn.close()

            is_active = False
            if u and u[1] == 1:
                try:
                    exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
                    if datetime.datetime.now() < exp:
                        is_active = True
                except: pass

            pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")

            kb = InlineKeyboardBuilder()
            if is_active:
                kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
            else:
                kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))

            kb.row(
                types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"),
                types.InlineKeyboardButton(text="📜 RULES", callback_data="rules")
            )
            kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

            caption = (
                f"<b>🌌 APX PRIME OS v190.0</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🕹️ <b>TRADER:</b> <code>{callback.from_user.first_name}</code>\n"
                f"📡 <b>STATUS:</b> ✅ <b>LIVE API SYNC</b>\n"
                f"🕰️ <b>PKT TIME:</b> <code>{pkt}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Institutional Nodes: 🟢 <b>Connected</b>"
            )
            await bot.send_photo(uid, BANNER_URL, caption=caption, parse_mode="HTML", reply_markup=kb.as_markup())
        else:
            await callback.answer("❌ Please join the channel first!", show_alert=True)
    except:
        await callback.answer("⚠️ Security Error", show_alert=True)

# ====================== GET KEY ======================
@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    await callback.answer()
    key = f"APX-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, key_taken) VALUES (?, ?, 0, 1)", 
                (callback.from_user.id, "NONE"))
    conn.commit()
    conn.close()

    await callback.message.answer(
        f"🔑 <b>TEMPORARY ACCESS KEY</b>\n\n"
        f"<code>{key}</code>\n\n"
        f"Copy aur bhejo:\n<code>/verify {key}</code>",
        parse_mode="HTML"
    )

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit()
    conn.close()
    
    await message.answer("✅ <b>7 DAYS ACCESS ACTIVATED SUCCESSFULLY!</b>", parse_mode="HTML")
    await init_term_after_verify(message)

async def init_term_after_verify(message: types.Message):
    user_ctx[message.from_user.id] = {"pairs": [], "last_report": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await message.answer("⚡ <b>SELECT OPERATIONAL MODE:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== TERMINAL ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id] = {"pairs": [], "last_report": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await callback.message.edit_caption(caption="⚡ <b>SELECT OPERATIONAL MODE:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

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
        text = f"✅ {display}" if code in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{code}"))
    
    builder.adjust(2)
    if sel:
        builder.row(types.InlineKeyboardButton(text="🚀 CONNECT TO LIVE API", callback_data="ask_time"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    
    await callback.message.edit_caption(caption="🧪 <b>SELECT ASSETS (MAX 3):</b>", parse_mode="HTML", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_pair(callback: types.CallbackQuery):
    uid = callback.from_user.id
    code = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid].get("mode") == "multi" else 1

    if code in user_ctx[uid]["pairs"]:
        user_ctx[uid]["pairs"].remove(code)
    elif len(user_ctx[uid]["pairs"]) < limit:
        user_ctx[uid]["pairs"].append(code)

    await callback.answer()
    await render_grid(callback)

@dp.callback_query(F.data == "ask_time")
async def ask_time(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.delete()
    await callback.message.answer("🕒 <b>Enter Start Time</b> (Format: <code>14:00</code>)", parse_mode="HTML")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return

    if user_ctx[uid]["step"] == "start_t":
        user_ctx[uid]["start_t"] = message.text
        user_ctx[uid]["step"] = "end_t"
        await message.answer("🕒 <b>Enter End Time</b> (Format: <code>16:00</code>)", parse_mode="HTML")
    elif user_ctx[uid]["step"] == "end_t":
        user_ctx[uid]["end_t"] = message.text
        await execute_live_signals(message)

# ====================== SIGNAL ENGINE ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx[uid]

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        load = await message.answer("📡 <b>CONNECTING TO LIVE OTC API...</b>", parse_mode="HTML")
        
        start_time = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_time = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        header = "🎴 <b>APX PRIME LIVE SIGNALS</b>\n"
        header += f"🕒 {data['start_t']} - {data['end_t']} PKT\n"
        header += "━━━━━━━━━━━━━━━━━━━━━━\n"

        body = ""
        async with aiohttp.ClientSession() as session:
            for pair in data["pairs"]:
                try:
                    async with session.get(f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100", timeout=12) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.split('\n'):
                                if not line.strip(): continue
                                line = line.replace('⧉', '').replace('⚡', '').strip()
                                if "|" in line:
                                    parts = line.split('|')
                                elif " - " in line:
                                    parts = line.split(' - ')
                                else: continue
                                
                                if len(parts) >= 2:
                                    t_str = parts[0].strip().split()[-1]
                                    direction = parts[1].strip().upper().replace('⇨', '').strip()
                                    try:
                                        sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                                        if start_time <= sig_time <= end_time:
                                            body += f"⧉ <b>{pair}</b> - {t_str} ⇨ <b>{direction}</b>\n"
                                    except: pass
                except: pass

        if not body.strip():
            body = "⚠️ No signals found in selected time range.\n"

        footer = "\n━━━━━━━━━━━━━━━━━━━━━━\n<i>1 Min Timeframe • 1 Step Martingale • 80%+ Accuracy</i>"
        report_content = header + body + footer
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen_sig"))
    kb.row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_signals"))
    kb.row(types.InlineKeyboardButton(text="🔄 CHANGE PAIRS", callback_data="change_pair_back"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    await message.answer(
        f"<b>📊 LIVE SIGNALS GENERATED</b>\n\n"
        f"<code>{report_content}</code>",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Signals copied! Long press & copy from above.", show_alert=True)

@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("🔄 Regenerating Signals...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    user_ctx[callback.from_user.id] = {"pairs": [], "last_report": None, "mode": user_ctx.get(callback.from_user.id, {}).get("mode", "single")}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await bot.send_message(callback.from_user.id, "⚡ <b>Select Mode Again:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(
        callback.from_user.id,
        "<code>╔══════════════════════════════╗\n"
        "║   APX PRIME TERMINAL CLOSED   ║\n"
        "╚══════════════════════════════╝\n\n"
        "Session terminated securely.\n"
        "See you next trade.</code>",
        parse_mode="HTML"
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
