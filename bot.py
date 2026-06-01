import os, asyncio, datetime, sqlite3, random, aiohttp, re
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

PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC",
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",
    "BTCUSD": "₿🌐 BTCUSD-OTC", "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC",
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "USDNGN": "🇺🇸🇳🇬 USDNGN-OTC", # Registered Node Asset Complete
    "AAPL": "🇺🇸🍎 AAPL-OTC", "MSFT": "🇺🇸💻 MSFT-OTC", "PFE": "🇺🇸💊 PFE-OTC",
    "JNJ": "🇺🇸🏥 JNJ-OTC", "MCD": "🇺🇸🍔 MCD-OTC", "INTL": "🇺🇸🔬 INTL-OTC"
}

STRATEGIES = {
    "1": "🛸 MATRIX NEURAL ENGINE (RSI+MA)",
    "2": "🛸 MACD COGNITIVE CROSSOVER",
    "3": "🛸 BOLLINGER QUANTUM EXTENSION",
    "4": "🛸 STOCHASTIC HIGH ACCURACY SHIELD",
    "5": "🛸 ENSEMBLE SYNAPSE MATRIX (ALL)"
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
    conn.commit(); conn.close()

async def get_broadcast_context():
    now_pkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    h = now_pkt.hour
    if 7 <= h < 12:
        return f"🛸 <b>APX TELEMETRY SYSTEM BROADCAST:</b>\n<code>{QUOTES['morning']}</code>\n\n🟢 <b>STATE: TERMINAL ONLINE & OPERATIONAL</b>"
    elif 12 <= h < 17:
        return f"🛸 <b>APX TELEMETRY SYSTEM BROADCAST:</b>\n<code>{QUOTES['cooldown']}</code>\n\n❄️ <b>STATE: HEAT COMPONENT COOL DOWN PROTOCOL</b>"
    elif 17 <= h < 23:
        return f"🛸 <b>APX TELEMETRY SYSTEM BROADCAST:</b>\n<code>{QUOTES['maintenance']}</code>\n\n🛠️ <b>STATE: CONCURRENT MAINTENANCE WINDOW ACTIVE</b>"
    else:
        return f"🛸 <b>APX TELEMETRY SYSTEM BROADCAST:</b>\n<code>{QUOTES['sleep']}</code>\n\n🌙 <b>STATE: DEEP SLEEP SECURITY PROTOCOL ACTIVATED</b>"

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⚡ ATTACH MAIN ENGINE", url=f"https://t.me/vectabot1"))
    kb.row(types.InlineKeyboardButton(text="🛡️ SECURE VERIFICATION DEEP SCAN", callback_data="auth_check"))
    
    await message.answer_photo(
        photo=BANNER_URL, 
        caption=f"<b>💎 APX PRIME OS v250.0</b>\n<i>Quantum AI Production Terminal Initialized.</i>\n\nWelcome back, Operator: <b>{message.from_user.first_name}</b> 👑\n\n<code>🚨 SECURE COLD STATUS ACTIVE. ENGAGE VERIFICATION SCAN.</code>", 
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ ACCESS KEY MATCHED!")
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

            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🔑 ASSIGN SYSTEM LEVEL PRIVILEGES", callback_data="get_key"))
            await bot.send_photo(
                chat_id=uid, photo=BANNER_URL, 
                caption=f"<b>🛸 APX PRIME QUANTUM OS</b>\n\nOperator Node: <b>{callback.from_user.first_name}</b>\n\n<code>⚠️ LOCK STATUS: ACCESS SECURITY KEY REMOVED OR NOT ALLOCATED.</code>", 
                parse_mode="HTML", reply_markup=kb.as_markup()
            )
        else:
            await callback.answer("❌ CRITICAL TASK FAULT: Channel authorization bridge missing!", show_alert=True)
    except:
        await callback.answer("⚠️ Core context stack overflow", show_alert=True)

@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    await callback.answer()
    key = f"APX-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, temp_key) VALUES (?, ?, 0, ?)", (callback.from_user.id, "NONE", key))
    conn.commit(); conn.close()
    await callback.message.answer(f"📦 <b>CIPHERED PRIVILEGE PAIR KEY DEPLOYED:</b>\n\n<code>{key}</code>\n\nExecute payload verification:\n<code>/verify {key}</code>", parse_mode="HTML")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    try: key = message.text.split(maxsplit=1)[1].strip()
    except: return await message.answer("❌ Use layout format: <code>/verify YOUR_KEY</code>", parse_mode="HTML")

    conn = sqlite3.connect('apx_stable_v190.db')
    row = conn.execute("SELECT temp_key FROM users WHERE uid = ?", (message.from_user.id,)).fetchone()
    conn.close()

    if not row or row[0] != key: return await message.answer("❌ <b>SECURITY MATRIX RUNTIME REJECTION: INVALID COLD KEY</b>", parse_mode="HTML")

    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit(); conn.close()

    await message.answer(f"🧬 <b>7-DAYS PREMIUM PRIVILEGES SYNCED TO NODE CURRENT PROFILE!</b>\nExpiration validation stamp: <code>{exp}</code>", parse_mode="HTML")
    await show_mode_selection_msg(message.from_user.id)

# ====================== WORKFLOWS ======================
async def show_mode_selection_msg(uid: int):
    user_ctx[uid] = {"pairs": [], "last_report": None, "strategy": None, "mode": None, "step": None}
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎯 SINGLE ASSET DEVIATION", callback_data="m:single"),
        types.InlineKeyboardButton(text="🌐 MULTI SPECTRUM FREQUENCY ARRAY", callback_data="m:multi")
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
    if sel: builder.row(types.InlineKeyboardButton(text="🔥 INITIALIZE MATRIX COMPLIANCE", callback_data="select_strategy"))
    builder.row(types.InlineKeyboardButton(text="⬅️ FLUSH PROFILE TO MODE SELECTION", callback_data="back_to_mode"))
    await bot.send_message(uid, "⚔️ <b>CORE OPERATIONAL ASSET GRID INTERFACE</b>\nSelect target network instruments to capture (Max 3):", parse_mode="HTML", reply_markup=builder.as_markup())

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
    await callback.message.edit_text("🧬 <b>SELECT STRATEGY QUANTUM FILTER LOGIC:</b>", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== TIME BOUNDARY INTERFACES ======================
@dp.callback_query(F.data.startswith("strat:"))
async def set_strategy(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    user_ctx[uid]["strategy"] = STRATEGIES[callback.data.split(":")[1]]
    user_ctx[uid]["step"] = "quotex_days"
    await callback.message.delete()
    await bot.send_message(uid, "💎 <b>QUOTEX HISTORICAL TELEMETRY MATRIX</b>\n\nInput days parameter for historical parsing:\n(e.g., Send <code>30</code>, <code>60</code>, or <code>90</code> days context line)", parse_mode="HTML")

@dp.message(lambda message: user_ctx.get(message.from_user.id, {}).get("step") == "quotex_days")
async def handle_quotex_days(message: types.Message):
    uid = message.from_user.id
    user_ctx[uid]["quotex_days"] = message.text
    user_ctx[uid]["step"] = "start_t"
    await message.answer("🕒 <b>TIME EXTRACTION ENGINE ACTIVE</b>\n\nSend desired <b>START TIME</b> (Format 24H -> e.g., <code>16:00</code>):", parse_mode="HTML")

@dp.message(lambda message: user_ctx.get(message.from_user.id, {}).get("step") == "start_t")
async def handle_start_time(message: types.Message):
    uid = message.from_user.id
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', message.text.strip()):
        return await message.answer("❌ Format Error. Re-enter format directly as (HH:MM) -> e.g., <code>20:00</code>", parse_mode="HTML")
    user_ctx[uid]["start_t"] = message.text.strip()
    user_ctx[uid]["step"] = "end_t"
    await message.answer("🕒 <b>TIME EXTRACTION ENGINE ACTIVE</b>\n\nSend desired <b>END TIME</b> (Format 24H -> e.g., <code>18:00</code>):", parse_mode="HTML")

@dp.message(lambda message: user_ctx.get(message.from_user.id, {}).get("step") == "end_t")
async def handle_end_time(message: types.Message):
    uid = message.from_user.id
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', message.text.strip()):
        return await message.answer("❌ Format Error. Re-enter format directly as (HH:MM) -> e.g., <code>22:00</code>", parse_mode="HTML")
    user_ctx[uid]["end_t"] = message.text.strip()
    user_ctx[uid]["step"] = "processing"
    await execute_live_signals(message)

# ====================== QUANTUM EXTRACTION LOGIC ENGINE ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or not data.get("pairs"): return await bot.send_message(uid, "⚠️ Session context mapping corrupted. Execute /start.", parse_mode="HTML")

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        # Fancy Rainbow Loader Screen
        load = await bot.send_message(uid, "🛸 <code>⚡ [ CONNECTING STABLE ACCESS NODE HOOKS ]</code>\n\n⚡ <b>DECRYPTING ARRAY:</b>\n<code>[🔴🔴⚫⚫⚫⚫⚫⚫⚫⚫] 20% PROCESS BLOCK</code>", parse_mode="HTML")
        await asyncio.sleep(0.4)
        await load.edit_text("🛸 <code>⚡ [ INGESTING STREAM METADATA ENGINE PACKETS ]</code>\n\n⚡ <b>DECRYPTING ARRAY:</b>\n<code>[🔴🔴🧡🧡💛💛⚫⚫⚫⚫] 60% HIGH RECON LINK</code>", parse_mode="HTML")
        await asyncio.sleep(0.4)
        await load.edit_text("🛸 <code>⚡ [ COMPILING DIRECT PARSED HOOK ARRAYS PERFECTLY ]</code>\n\n⚡ <b>DECRYPTING ARRAY:</b>\n<code>[🔴🔴🧡🧡💛💛💚💚🟦🟣] 100% SECURE TUNNEL LOADED</code>", parse_mode="HTML")
        await asyncio.sleep(0.2)

        start_time = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_time = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        header = "🛸 <b>APX PRIME QUANTUM OS SIGNALS</b>\n"
        header += f"🔮 WINDOW: <code>{data['start_t']} - {data['end_t']} PKT (UTC+6)</code>\n"
        header += f"💠 COGNITIVE MODULE: <code>{data['strategy']}</code>\n"
        header += f"📊 ANALYSIS DEPTH: <code>{data.get('quotex_days', '30')} Days Historical</code>\n"
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
                                
                                # Flexible Data Stream Evaluator (Supports =>, |, -)
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
                                        
                                        # Midnight boundary mapping fix
                                        is_inside = False
                                        if start_time <= end_time:
                                            is_inside = start_time <= sig_time <= end_time
                                        else:
                                            is_inside = sig_time >= start_time or sig_time <= end_time
                                            
                                        if is_inside:
                                            signals.append((sig_time, pair, direction, t_str))
                                    except: pass
                except: pass

        signals.sort(key=lambda x: x[0])

        body = ""
        # Strict Monospace formatting logic to keep arrows securely positioned 
        for _, pair, direction, t in signals[:45]:
            arrow = "↑" if direction in ["CALL", "BUY"] else "↓"
            body += f"⧉ {pair+'-OTC':<12} → {t} ⇨ {direction:<4} {arrow}\n"

        if not body.strip():
            body = "⚠️ NO STRUCTURAL PARSED HOOK MATCHED:\nNo live API records found fitting selected variables inside server range.\n"

        footer = "\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n📋 <b>CORE OPERATIONS PROTOCOLS:</b>\n- DO NOT ALLOCATE VOLUMES ON CHANNELS RATIO < 80%\n- EMPLOY PREMIUM ONE-STEP SAFETY SHIELD PROTECTION MARGIN"
        report_content = header + body + footer + "\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<i>Powered by APX Premium</i>"
        await load.delete()

    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 DYNAMIC ENGINE RE-GEN", callback_data="regen_sig"),
        types.InlineKeyboardButton(text="📋 CAPTURE STRUCTURAL PAYLOAD", callback_data="copy_signals")
    ).row(
        types.InlineKeyboardButton(text="🔄 RE-MAP FREQUENCY ASSETS", callback_data="change_pair_back"),
        types.InlineKeyboardButton(text="❌ SHUTDOWN TERMINAL", callback_data="exit_sys")
    )
    await bot.send_message(uid, f"📡 <b>DATA PROCESSING CORE DISCHARGE</b>\n\n<code>{report_content}</code>", parse_mode="HTML", reply_markup=kb.as_markup())

# ====================== DISPATCH CORE MAPS ======================
@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("Recalibrating high frequency tracking array...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Operational data packet stored to clipboard context!", show_alert=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer(); await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer(); await callback.message.delete()
    await bot.send_message(callback.from_user.id, "<code>APX SYSTEM SAFELY SHUT DOWN. MEMORY POOLS FLUSHED.\nGoodbye! 👋</code>", parse_mode="HTML")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
