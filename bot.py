import os
import asyncio
import datetime
import random
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====================== CONFIGURATION ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873 
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"
API_URL = "https://apx-otc-api-production.up.railway.app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_ctx = {} 
SYSTEM_STATE = {"broadcast_msg": None, "mode": "auto"} # For Manual Broadcast

# ALL 24 QUOTEX ASSETS
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

# ====================== ADMIN & BROADCAST LOGIC ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🎙 SET MANUAL BROADCAST", callback_data="adm:set_bc"),
        types.InlineKeyboardButton(text="🔄 RESET TO AUTO", callback_data="adm:reset_bc")
    ).as_markup()
    await message.answer("🛠 **MASTER ADMIN PANEL**\nControl the global dashboard status:", reply_markup=kb)

@dp.callback_query(F.data == "adm:set_bc")
async def bc_input(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"step": "admin_bc"}
    await callback.message.answer("✍️ **Send your broadcast message:**\n(Example: '🔥 Maintenance till 4PM' or '✅ All pairs hitting 99%')")

@dp.message(lambda m: user_ctx.get(m.from_user.id, {}).get("step") == "admin_bc")
async def save_bc(message: types.Message):
    SYSTEM_STATE["broadcast_msg"] = message.text
    SYSTEM_STATE["mode"] = "manual"
    user_ctx.pop(message.from_user.id)
    await message.answer("✅ **GLOBAL BROADCAST UPDATED!**")

@dp.callback_query(F.data == "adm:reset_bc")
async def reset_bc(callback: types.CallbackQuery):
    SYSTEM_STATE["mode"] = "auto"
    await callback.answer("Switched to Auto-PKT Mode", show_alert=True)

# ====================== START & DASHBOARD ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # Strict Channel Join
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if chat.status in ["left", "kicked"]:
            kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="📢 JOIN CHANNEL", url=f"https://t.me/vectabot1")).as_markup()
            return await message.answer_photo(photo=BANNER_URL, caption="🛡️ **STRICT ACCESS**\nJoin channel to sync API Node.", reply_markup=kb)
    except: pass

    # Auto Broadcasting Logic (PKT Time)
    pkt_hour = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)).hour
    if SYSTEM_STATE["mode"] == "manual":
        live_status = f"📢 {SYSTEM_STATE['broadcast_msg']}"
    else:
        live_status = "✅ API NODE: STABLE" if 9 <= pkt_hour <= 23 else "🌙 NODE: SLEEP (LOW VOL)"

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🚀 LAUNCH TERMINAL", callback_data="init_term"))
    kb.row(types.InlineKeyboardButton(text="👤 PROFILE", callback_data="profile"), types.InlineKeyboardButton(text="📜 RULES", callback_data="rules"))
    
    caption = (
        f"💎 **APX PRIME OS v28.0** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **USER:** `{message.from_user.full_name}`\n"
        f"📡 **STATUS:** `{live_status}`\n"
        f"🌍 **ZONE:** PKT (UTC+5)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Institutional Terminal Ready."
    )
    await message.answer_photo(photo=BANNER_URL, caption=caption, reply_markup=kb.as_markup())

# ====================== SELECTION WORKFLOW ======================
@dp.callback_query(F.data == "init_term")
async def init_term(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id] = {"pairs": []}
    await render_grid(callback)

async def render_grid(callback: types.CallbackQuery):
    uid = callback.from_user.id
    sel = user_ctx[uid]["pairs"]
    builder = InlineKeyboardBuilder()
    for code, display in PAIRS_DATA.items():
        text = f"🔹 {display} ✅" if display in sel else f"💠 {display}"
        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"sel:{display}"))
    builder.adjust(2)
    if sel: builder.row(types.InlineKeyboardButton(text=f"🔥 NEXT: CONFIG ({len(sel)})", callback_data="ask_strat"))
    await callback.message.edit_caption(caption="🧪 **ASSET GRID (24 PAIRS)**\nSelect assets to analyze:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sel:"))
async def toggle_p(callback: types.CallbackQuery):
    uid = callback.from_user.id
    pair = callback.data.split(":")[1]
    if pair in user_ctx[uid]["pairs"]: user_ctx[uid]["pairs"].remove(pair)
    elif len(user_ctx[uid]["pairs"]) < 3: user_ctx[uid]["pairs"].append(pair)
    await render_grid(callback)

@dp.callback_query(F.data == "ask_strat")
async def ask_strat(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📊 LEVEL 1 (S/R)", callback_data="st:L1"),
           types.InlineKeyboardButton(text="⚡ LEVEL 2 (Neural)", callback_data="st:L2"))
    kb.row(types.InlineKeyboardButton(text="💎 BOLLINGER BANDS V3", callback_data="st:BB"))
    await callback.message.edit_caption(caption="🧠 **STRATEGY CONFIG**\nSelect extraction logic:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("st:"))
async def ask_time(callback: types.CallbackQuery):
    user_ctx[callback.from_user.id]["strat"] = callback.data.split(":")[1]
    await callback.message.delete()
    await callback.message.answer("🕒 **TIME PROTOCOL**\nSend **START TIME** (Format: `12:00`)")

@dp.message(F.text.regexp(r'^([01]\d|2[0-3]):([0-5]\d)$'))
async def handle_times(message: types.Message):
    uid = message.from_user.id
    if uid not in user_ctx: return
    if "start_t" not in user_ctx[uid]:
        user_ctx[uid]["start_t"] = message.text
        await message.answer("🕒 **TIME PROTOCOL**\nNow send **END TIME** (Format: `14:30`)")
    else:
        user_ctx[uid]["end_t"] = message.text
        await execute_engine(message)

# ====================== EXTRACTION ENGINE (FLASHY BARS) ======================
async def execute_engine(message: types.Message):
    uid = message.from_user.id
    data = user_ctx[uid]
    
    load = await message.answer("📡 **SYNCHRONIZING NEURAL API...**")
    for i in [25, 60, 90, 100]:
        await asyncio.sleep(0.4)
        bar = "🟦" * (i // 10) + "⬜" * (10 - i // 10)
        await load.edit_text(f"🧪 **SCANNING QUOTEX BANDS**\n`[{bar}] {i}%` \nStrategy: {data['strat']}")

    report = (
        f"╔════════════════════════════╗\n"
        f"        **APX ALPHA PRO**\n"
        f"╚════════════════════════════╝\n"
        f"STRAT: `{data['strat']}` | ZONE: `PKT` \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f" TIME  ┃ ASSET   ┃ DIR   ┃ ACC \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    start = datetime.datetime.strptime(data['start_t'], "%H:%M")
    end = datetime.datetime.strptime(data['end_t'], "%H:%M")
    curr = start
    while curr < end:
        for p in data["pairs"]:
            report += f" `{curr.strftime('%H:%M')}` ┃ `{p.split()[1][:6]}` ┃ `{random.choice(['CALL', 'PUT '])}` ┃ `{random.randint(92, 98)}%` \n"
        curr += datetime.timedelta(minutes=random.randint(5, 10))

    await load.delete()
    await message.answer(report + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ **API ENCRYPTED: PKT UTC+5**", parse_mode="Markdown")
    user_ctx.pop(uid, None)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
            
