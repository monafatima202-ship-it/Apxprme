import os, asyncio, datetime, sqlite3, random, aiohttp, re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN", "")
bot = Bot(token=TOKEN, default_properties=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_ctx = {}

# FULL 24 ASSETS WITH DUAL FLAGS
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC", 
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",   
    "BTCUSD": "₿🌐 BTCUSD-OTC", "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC", 
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "AAPL": "🇺🇸🍎 AAPL-OTC", "MSFT": "🇺🇸💻 MSFT-OTC", "PFE": "🇺🇸💊 PFE-OTC", "JNJ": "🇺🇸🏥 JNJ-OTC",
    "MCD": "🇺🇸🍔 MCD-OTC", "INTL": "🇺🇸🔬 INTL-OTC"
}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_ctx[message.from_user.id] = {}
    await message.answer("🔢 <b>Enter Number of Days (Subscription):</b>")
    user_ctx[message.from_user.id]["step"] = "days"

@dp.message(F.text.regexp(r'^\d+$'))
async def handle_days(message: types.Message):
    user_ctx[message.from_user.id]["days"] = message.text
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI ASSET", callback_data="m:multi"))
    await message.answer("⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("m:"))
async def mode_set(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["mode"] = callback.data.split(":")[1]
    user_ctx[callback.from_user.id]["pairs"] = []
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        builder.add(types.InlineKeyboardButton(text=display, callback_data=f"sel:{code}"))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="🚀 CONFIRM & NEXT", callback_data="ask_time"))
    await callback.message.edit_text("🧪 <b>SELECT ASSETS:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle(callback: types.CallbackQuery):
    code = callback.data.split(":")[1]
    pairs = user_ctx[callback.from_user.id]["pairs"]
    if code in pairs: pairs.remove(code)
    else: pairs.append(code)
    await callback.answer(f"Selected: {len(pairs)}")

@dp.callback_query(F.data == "ask_time")
async def ask_t(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["step"] = "start_t"
    await callback.message.edit_text("🕒 <b>Enter Start Time (HH:MM):</b>")

@dp.message(F.text.regexp(r'^\d{2}:\d{2}$'))
async def handle_time(message: types.Message):
    ctx = user_ctx[message.from_user.id]
    if ctx["step"] == "start_t":
        ctx["start_t"] = message.text
        ctx["step"] = "end_t"
        await message.answer("🕒 <b>Enter End Time (HH:MM):</b>")
    else:
        ctx["end_t"] = message.text
        await execute_signals(message)

async def execute_signals(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    msg = await message.answer("🌌 <b>APX QUANTUM SYNCING...</b>\n<code>[▓▓▓▓▓▓▓▓▓▓] 100%</code>")
    
    start = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
    end = datetime.datetime.strptime(data['end_t'], "%H:%M").time()
    
    body = ""
    async with aiohttp.ClientSession() as session:
        for pair in data["pairs"]:
            async with session.get(f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100") as resp:
                text = await resp.text()
                for line in text.splitlines():
                    # Fixed Regex for your exact API structure
                    match = re.search(r'(\d{2}:\d{2}).*?(CALL|PUT|BUY|SELL)', line, re.IGNORECASE)
                    if match:
                        t_str, direction = match.groups()
                        sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                        if start <= sig_time <= end:
                            arrow = "↑" if direction.upper() in ["CALL", "BUY"] else "↓"
                            # Fixed Width: Pair(12) + Time(5) + Dir(4) + Arrow(1)
                            body += f"⧉ {pair+'-OTC':<12} → {t_str} ⇨ {direction.upper():<4} {arrow}\n"
    
    if not body: body = "⚠️ No signals found in range.\n"
    
    report = (
        f"<b>📡 LIVE SIGNALS GENERATED</b>\n"
        f"🕒 {data['start_t']} - {data['end_t']} PKT\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<code>{body}</code>"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Powered by APX Premium</i>"
    )
    await msg.edit_text(report, reply_markup=InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen"),
        types.InlineKeyboardButton(text="📋 COPY", callback_data="copy")
    ).as_markup())

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
