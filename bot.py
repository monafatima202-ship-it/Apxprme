import os
import asyncio
import datetime
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

# HTML Mode global property fix to render clean layout
bot = Bot(token=TOKEN, default_properties=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
user_ctx = {} 

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
    conn = sqlite3.connect('apx_ultimate_v180.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, key_taken INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    uid = message.from_user.id
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1"))
    kb.row(types.InlineKeyboardButton(text="🛡️ VERIFY MEMBERSHIP", callback_data="auth_check"))
    
    await message.answer_photo(
        photo=BANNER_URL, 
        caption="<b>🛡️ STRICT SECURITY PROTOCOL</b>\n\nYour session needs validation. Please join the channel and click verify to initialize the terminal.", 
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ Verification Successful!", show_alert=False)
            await callback.message.delete()
            
            conn = sqlite3.connect('apx_ultimate_v180.db')
            u = conn.execute("SELECT expiry, is_vip, key_taken FROM users WHERE uid = ?", (uid,)).fetchone()
            conn.close()
            
            is_active = False
            if u and u[1] == 1:
                exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
                if datetime.datetime.now() < exp: is_active = True

            pkt = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).strftime("%H:%M")
            
            kb = InlineKeyboardBuilder()
            if is_active:
                kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
            elif not u or u[2] == 0:
                kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))
            else:
                kb.row(types.InlineKeyboardButton(text="🔒 ACCESS EXPIRED", callback_data="profile"))

            kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
            kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

            caption = (
                f"🌌 <b>APX PRIME OS v180.0</b> 🌌\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🕹️ <b>TRADER:</b> <code>{callback.from_user.first_name}</code>\n"
                f"📡 <b>STATUS:</b> ✅ <b>LIVE API SYNC</b>\n"
                f"🕰️ <b>PKT TIME:</b> <code>{pkt}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Institutional Nodes: 🟢 <b>Connected</b>"
            )
            await bot.send_photo(chat_id=uid, photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())
        else:
            await callback.answer("❌ Verification Failed! Please join the channel first.", show_alert=True)
    except Exception as e:
        await callback.answer("⚠️ Security Error: Context reset.", show_alert=True)

# ====================== TERMINAL CORE WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    await callback.answer()
    user_ctx[callback.from_user.id] = {"pairs": [], "last_report": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await callback.message.edit_caption(caption="⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb.as_markup())

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
        text = f"✅ {code}" if code in sel else f"💠 {code}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{code}"))
    builder.adjust(2) 
    if sel: 
        builder.row(types.InlineKeyboardButton(text="🚀 CONNECT TO LIVE API", callback_data="ask_time"))
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    await callback.message.edit_caption(caption="🧪 <b>SELECT ASSETS (MAX 3):</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    code = callback.data.split(":")[1]
    limit = 3 if user_ctx[uid]["mode"] == "multi" else 1
    
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
    await callback.message.answer("🕒 <b>LIVE PROTOCOL</b>\nSend Start Time (e.g. <code>14:00</code>)")

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
        await execute_live_signals(message)

# ====================== STRICT API FILTER LOGIC ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id if isinstance(message, types.Message) else message.from_user.id
    msg_obj = message if isinstance(message, types.Message) else message.message
    data = user_ctx[uid]

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        load = await msg_obj.answer("📡 <b>CONNECTING TO LIVE OTC API...</b>")
        
        header = "🎴 UTC/GMT : ( +6:00 ) 🇧🇩\n🎴 1STEP MARTINGALE\n🎴 1MINUTE TIMEFRAME\n\n"
        body = ""
        
        # User ka select kiya hua time criteria format mein lane ke liye conversion
        start_time = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_time = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        async with aiohttp.ClientSession() as session:
            for pair_code in data["pairs"]:
                api_url = f"https://milongazi197.serv00.net/f/api.php?pair={pair_code}-OTC&count=100"
                try:
                    async with session.get(api_url, timeout=10) as response:
                        if response.status == 200:
                            raw_text = await response.text()
                            lines = raw_text.split('\n')
                            for line in lines:
                                if not line.strip(): continue
                                
                                # Clean character variations if any and check split conditions
                                line_clean = line.replace('⧉', '').replace('⚡', '').strip()
                                
                                if "|" in line_clean:
                                    parts = line_clean.split('|')
                                elif " - " in line_clean:
                                    parts = line_clean.split(' - ')
                                else:
                                    continue
                                    
                                if len(parts) >= 2:
                                    # Phele part se time extraction aur safe processing
                                    sig_time_str = parts[0].strip().replace('⧉', '').strip()
                                    if " " in sig_time_str: 
                                        sig_time_str = sig_time_str.split()[-1]
                                        
                                    sig_dir = parts[1].strip().upper().replace('⇨', '').strip()
                                    
                                    try:
                                        # Strict check framework matching criteria
                                        sig_time = datetime.datetime.strptime(sig_time_str, "%H:%M").time()
                                        if start_time <= sig_time <= end_time:
                                            body += f"⧉ {pair_code:8}-OTC - {sig_time_str} ⇨ {sig_dir}\n"
                                    except: pass
                except Exception as e:
                    print(f"API Request failure: {e}")

        if not body.strip():
            body = "⚠️ No live data matched within the selected parameters in API.\n"

        footer = "\nRULES ‼️\n- DO NOT TRADE IN MARKET THAT ARE LESS THEN 80%\n- USE SEFTY MARGIN FOR BETTER ACCURACY"
        report_content = header + body + footer
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔄 REGENERATE SIGNALS", callback_data="regen_sig"),
           types.InlineKeyboardButton(text="🔄 CHANGE PAIR", callback_data="change_pair_back"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT TERMINAL", callback_data="exit_sys"))

    final_msg = f"📋 <b>TAP TO COPY SIGNALS:</b>\n\n<code>{report_content}</code>"
    
    if is_regen: 
        await msg_obj.edit_text(final_msg, reply_markup=kb.as_markup())
    else: 
        await msg_obj.answer(final_msg, reply_markup=kb.as_markup())

# ====================== UTILS & BACKLOG RECOVERY ======================
@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    
    uid = callback.from_user.id
    user_ctx[uid] = {"pairs": [], "last_report": None, "mode": user_ctx.get(uid, {}).get("mode", "single")}
    
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        builder.add(types.InlineKeyboardButton(text=f"💠 {code}", callback_data=f"sel:{code}"))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="⬅️ BACK", callback_data="init_term"))
    
    await bot.send_photo(chat_id=uid, photo=BANNER_URL, caption="🧪 <b>SELECT ASSETS (MAX 3):</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("Synchronizing strict data stream...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    await callback.answer()
    key = f"APX-{random.randint(1000, 9999)}-VIP"
    conn = sqlite3.connect('apx_ultimate_v180.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, key_taken) VALUES (?, ?, 0, 1)", (callback.from_user.id, "NONE"))
    conn.commit(); conn.close()
    await callback.message.answer(f"🔑 <b>TAP TO COPY KEY:</b>\n\n<code>/verify {key}</code>")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_ultimate_v180.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit(); conn.close()
    await message.answer("✅ <b>AUTHORIZED</b>")
    
    class ProxyCall:
        def __init__(self, msg):
            self.from_user = msg.from_user
            self.message = msg
    await show_dashboard(ProxyCall(message))

@dp.callback_query(F.data == "exit_sys")
async def exit_cb(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    exit_text = (
        "<code>"
        "╔════════════════════════════════════════╗\n"
        "║       APX PRIME TERMINAL DISCONNECTED  ║\n"
        "╚════════════════════════════════════════╝\n"
        "  ● Node Status  : [ OFFLINE ]\n"
        "  ● Core Session : [ TERMINATED ]\n\n"
        "  → System closed securely. See you next session. "
        "</code>"
    )
    await bot.send_message(chat_id=callback.from_user.id, text=exit_text)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
