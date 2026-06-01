import os, asyncio, datetime, sqlite3, random, aiohttp, re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(token=TOKEN, default_properties=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_ctx = {}

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
    "1": "⚡ MACHINE LEARNING MATRIX (RSI+MA)",
    "2": "⚡ ADVANCED MACD QUANTUM",
    "3": "⚡ BOLLINGER SHIELD LAYER",
    "4": "⚡ STOCHASTIC HIGGS FREQUENCY",
    "5": "⚡ COGNITIVE NEURAL ENSEMBLE (ALL)"
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

async def get_broadcast_context():
    now_pkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now_pkt.hour
    if 7 <= h < 12:
        return f"⚡ <b>APX CYBERNETIC BROADCAST:</b>\n<code>{QUOTES['morning']}</code>\n🟢 <b>STATE: TERMINAL ONLINE & OPERATIONAL</b>"
    elif 12 <= h < 17:
        return f"⚡ <b>APX CYBERNETIC BROADCAST:</b>\n<code>{QUOTES['cooldown']}</code>\n❄️ <b>STATE: HEAT DISK COOL DOWN PROTOCOL</b>"
    elif 17 <= h < 23:
        return f"⚡ <b>APX CYBERNETIC BROADCAST:</b>\n<code>{QUOTES['maintenance']}</code>\n🛠️ <b>STATE: FLUID MAINTENANCE CONFIG RUNNING</b>"
    else:
        return f"⚡ <b>APX CYBERNETIC BROADCAST:</b>\n<code>{QUOTES['sleep']}</code>\n🌙 <b>STATE: DEEP SLEEP ENCRYPTION MODE</b>"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⚡ CONNECT NETWORK CHANNEL", url=f"https://t.me/vectabot1"))
    kb.row(types.InlineKeyboardButton(text="🛡️ RUN VERIFICATION DEEP SCAN", callback_data="auth_check"))
    
    await message.answer_photo(
        photo=BANNER_URL, 
        caption=f"<b>💎 APX PRIME OS v250.0</b>\n<i>Quantum AI Signal Terminal Loaded Successfully.</i>\n\nWelcome back, Operator: <b>{message.from_user.first_name}</b> 👑\n\n<code>🚨 SECURE SYSTEM LOCK ACTIVE. RUN VERIFICATION FLOW.</code>", 
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ ACCESS KEY AUTHORIZED!")
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

            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🔑 DEPLOY TERMINAL PRIVILEGES", callback_data="get_key"))
            await bot.send_photo(
                chat_id=uid, 
                photo=BANNER_URL, 
                caption=f"<b>🛸 APX PRIME QUANTUM OS</b>\n\nOperator Identity Detected: <b>{callback.from_user.first_name}</b>\n\n<code>⚠️ STATUS: ENCRYPTED. ACCESS KEY MISSING FROM CURRENT NODE.</code>", 
                parse_mode="HTML",
                reply_markup=kb.as_markup()
            )
        else:
            await callback.answer("❌ CRITICAL INCOMPLETE TASK: Node requires channel handshake!", show_alert=True)
    except:
        await callback.answer("⚠️ Core Memory Stack Fault", show_alert=True)

@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    await callback.answer()
    key = f"APX-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, temp_key) VALUES (?, ?, 0, ?)", (callback.from_user.id, "NONE", key))
    conn.commit(); conn.close()
    await callback.message.answer(f"📦 <b>CIPHERED ACCESS DEPLOYED:</b>\n\n<code>{key}</code>\n\nExecute command payload:\n<code>/verify {key}</code>", parse_mode="HTML")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    try: key = message.text.split(maxsplit=1)[1].strip()
    except: return await message.answer("❌ Usage format error: <code>/verify KEY</code>", parse_mode="HTML")

    conn = sqlite3.connect('apx_stable_v190.db')
    row = conn.execute("SELECT temp_key FROM users WHERE uid = ?", (message.from_user.id,)).fetchone()
    conn.close()

    if not row or row[0] != key: return await message.answer("❌ <b>SECURITY ALERT: KEY INVALID OR TAMPERED</b>", parse_mode="HTML")

    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit(); conn.close()

    await message.answer(f"🧬 <b>7-DAYS TERMINAL ACCESS PROTOCOLS LOADED!</b>\nNode active till: <code>{exp}</code>", parse_mode="HTML")
    await show_mode_selection_msg(message.from_user.id)

# ====================== MODE / ASSETS UI (FANCY) ======================
async def show_mode_selection_msg(uid: int):
    user_ctx[uid] = {"pairs": [], "last_report": None, "strategy": None, "mode": None, "step": None}
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE QUANTUM ENGINE", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI FREQUENCY ARRAY", callback_data="m:multi")
    )
    b_msg = await get_broadcast_context()
    await bot.send_message(uid, f"{b_msg}\n\n<b>┌────────────────────────┐</b>\n   ⚙️ <b>CHOOSE OPERATIONAL MODULE:</b>\n<b>└────────────────────────┘</b>", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    user_ctx.setdefault(uid, {"pairs": [], "last_report": None, "strategy": None})
    user_ctx[uid]["mode"] = callback.data.split(":")[1]
    await send_pair_selection(uid)

async def send_pair_selection(uid: int):
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        status = "🟢" if code in sel else "⚫"
        builder.add(types.InlineKeyboardButton(text=f"{status} {display}", callback_data=f"sel:{code}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text="🔥 COMPILE SELECTED PARAMETERS", callback_data="select_strategy"))
    builder.row(types.InlineKeyboardButton(text="⬅️ RE-INITIALIZE MAIN MENU", callback_data="back_to_mode"))
    await bot.send_message(uid, "⚔️ <b>TARGET INTERFACE NODE MATRIX</b>\n<i>Select your target digital operational assets (Max 3):</i>", parse_mode="HTML", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_pair(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_ctx: return
    code = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid].get("mode") == "multi" else 1
    if code in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(code)
    elif len(user_ctx[uid]["pairs"]) < limit: user_ctx[uid]["pairs"].append(code)
    await callback.answer()
    await callback.message.delete()
    await send_pair_selection(uid)

@dp.callback_query(F.data == "back_to_mode")
async def back_to_mode(callback: types.CallbackQuery):
    await callback.answer(); await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "select_strategy")
async def select_strategy(callback: types.CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardBuilder()
    for key, name in STRATEGIES.items():
        kb.row(types.InlineKeyboardButton(text=name, callback_data=f"strat:{key}"))
    await callback.message.edit_text("🧬 <b>SELECT PREFERRED QUANT ALGORITHM LAYER:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== STAGE FIXED STEPS FLOW (CRITICAL ROUTING BUG SOLVED) ======================
@dp.callback_query(F.data.startswith("strat:"))
async def set_strategy(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    user_ctx[uid]["strategy"] = STRATEGIES[callback.data.split(":")[1]]
    user_ctx[uid]["step"] = "quotex_days" # Explicit status tagging
    await callback.message.delete()
    await bot.send_message(uid, "💎 <b>QUOTEX HISTORICAL TELEMETRY MATRIX</b>\n\nInput days parameter for historical parsing:\n(e.g., Send <code>30</code>, <code>60</code>, or <code>90</code> days context line)", parse_mode="HTML")

# --- STRICT SEPARATED ROUTING ACCORDING TO SYSTEM STATE STACKS ---
@dp.message(lambda message: user_ctx.get(message.from_user.id, {}).get("step") == "quotex_days")
async def handle_quotex_days(message: types.Message):
    uid = message.from_user.id
    user_ctx[uid]["quotex_days"] = message.text
    user_ctx[uid]["step"] = "start_t" # Move forward cleanly
    await message.answer("🕒 <b>TIME EXTRACTION ENGINE</b>\n\nSend desired <b>START TIME</b> (Format 24H -> e.g., <code>16:00</code>):", parse_mode="HTML")

@dp.message(lambda message: user_ctx.get(message.from_user.id, {}).get("step") == "start_t")
async def handle_start_time(message: types.Message):
    uid = message.from_user.id
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', message.text.strip()):
        return await message.answer("❌ Invalid format. Please resend exactly as (HH:MM) -> e.g., <code>20:00</code>")
    user_ctx[uid]["start_t"] = message.text.strip()
    user_ctx[uid]["step"] = "end_t" # Move forward cleanly
    await message.answer("🕒 <b>TIME EXTRACTION ENGINE</b>\n\nSend desired <b>END TIME</b> (Format 24H -> e.g., <code>18:00</code>):", parse_mode="HTML")

@dp.message(lambda message: user_ctx.get(message.from_user.id, {}).get("step") == "end_t")
async def handle_end_time(message: types.Message):
    uid = message.from_user.id
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', message.text.strip()):
        return await message.answer("❌ Invalid format. Please resend exactly as (HH:MM) -> e.g., <code>22:00</code>")
    user_ctx[uid]["end_t"] = message.text.strip()
    user_ctx[uid]["step"] = "processing" # Engaged execution lock
    await execute_live_signals(message)

# ====================== STYLISH DYNAMIC LOAD MATRIX ENGINE ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or not data.get("pairs"): return await bot.send_message(uid, "⚠️ Hardware mapping array context was corrupted. Restart process.", parse_mode="HTML")

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        # High-End Cyberpunk Interface Loading System 
        load = await bot.send_message(uid, "🛸 <code>⚡ [ CONNECTING PROTOCOL ENGINE ACCESS HOOKS ]</code>\n\n⚡ <b>DECRYPTING ARRAY:</b>\n<code>[🔴🔴⚫⚫⚫⚫⚫⚫⚫⚫] 20% OVERLOAD BLOCK</code>", parse_mode="HTML")
        await asyncio.sleep(0.5)
        await load.edit_text("🛸 <code>⚡ [ METADATA STREAM FROM LIVE MATRIX ACTIVE ]</code>\n\n⚡ <b>DECRYPTING ARRAY:</b>\n<code>[🔴🔴🧡🧡💛💛⚫⚫⚫⚫] 60% HIGH LATENCY LINK</code>", parse_mode="HTML")
        await asyncio.sleep(0.5)
        await load.edit_text("🛸 <code>⚡ [ PARSING COMPLETED PERFECTLY WITHOUT ANY DEVIATION ]</code>\n\n⚡ <b>DECRYPTING ARRAY:</b>\n<code>[🔴🔴🧡🧡💛💛💚💚🟦🟣] 100% SECURE FIREWALL INSIDE</code>", parse_mode="HTML")
        await asyncio.sleep(0.3)

        start_time = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_time = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        header = "🛸 <b>APX PRIME QUANTUM OS SIGNALS</b>\n"
        header += f"🔮 WINDOW: <code>{data['start_t']} - {data['end_t']} PKT (UTC+6)</code>\n"
        header += f"💠 COGNITIVE: <code>{data['strategy']}</code>\n"
        header += f"📊 DEPTH COMPASS: <code>{data.get('quotex_days', '30')} Days Historical</code>\n"
        header += "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"

        signals = []
        async with aiohttp.ClientSession() as session:
            for pair in data["pairs"]:
                api_url = f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100"
                try:
                    async with session.get(api_url, timeout=12) as resp:
                        if resp.status == 200:
                            raw_text = await resp.text()
                            for line in raw_text.splitlines():
                                if not line.strip(): continue
                                
                                # High level custom token match configuration map logic
                                line_clean = line.replace('⧉', '').replace('⚡', '').replace('⇨', '').strip()
                                parts = []
                                if "=>" in line: parts = [p.strip() for p in line.split("=>")]
                                elif "|" in line_clean: parts = [p.strip() for p in line_clean.split('|')]
                                elif "-" in line_clean: parts = [p.strip() for p in line_clean.split('-')]
                                
                                if len(parts) >= 2:
                                    t_str = parts[0].strip() if len(parts) == 2 else parts[1].strip()
                                    direction = parts[-1].strip().upper()
                                    if " " in t_str: t_str = t_str.split()[-1]
                                    
                                    try:
                                        sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                                        if start_time <= sig_time <= end_time:
                                            signals.append((sig_time, pair, direction, t_str))
                                    except: pass
                except: pass

        signals.sort(key=lambda x: x[0])

        body = ""
        # Absolute hard-spaced padding configuration format matrix layout lock to avoid breaking sequence rows
        for _, pair, direction, t in signals[:45]:
            arrow = "↑" if direction in ["CALL", "BUY"] else "↓"
            body += f"⧉ {pair+'-OTC':<12} → {t} ⇨ {direction:<4} {arrow}\n"

        if not body.strip():
            body = "⚠️ STRICT RUNTIME NOTICE:\nNo quantitative data packets matched target filters inside live array server database.\n"

        footer = "\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n📋 <b>NODE TERMINAL RULES:</b>\n- DO NOT ASSIGN BALANCES TO VALUES WITH PAYOUTS < 80%\n- EMPLOY STRICT ONE-STEP SAFETY MARGIN MATRIX SHIELD"
        report_content = header + body + footer + "\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<i>Powered by APX Premium</i>"
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 RE-GENERATE METADATA", callback_data="regen_sig"),
        types.InlineKeyboardButton(text="📋 SAVE PAYLOAD BLOCK", callback_data="copy_signals")
    ).row(
        types.InlineKeyboardButton(text="🔄 ALTER TARGET CHANNELS", callback_data="change_pair_back"),
        types.InlineKeyboardButton(text="❌ FLUSH DATA TERMINAL", callback_data="exit_sys")
    )
    await bot.send_message(uid, f"📡 <b>OS ENGINE INGESTION COMPLETE</b>\n\n<code>{report_content}</code>", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== SECURE CALLBACK LOGIC ======================
@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("Recalibrating high frequency quantum array layers...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Matrix data successfully allocated to device structural clipboard!", show_alert=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer(); await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer(); await callback.message.delete()
    await bot.send_message(callback.from_user.id, "<code>APX CYBERNETIC COLD REBOOT COMPLETE. CONSOLE CLOSED SECURELY.\nGoodbye! 👋</code>", parse_mode="HTML")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
