"""
YUYU ADS - Telegram Booking Bot
Billboard/OOH ad slot booking with bank transfer + screenshot confirmation.

SETUP:
1. pip install python-telegram-bot --break-system-packages --upgrade
2. Get a bot token from @BotFather on Telegram (message it, /newbot, follow steps)
3. Paste your token into BOT_TOKEN below
4. Edit BILLBOARDS list with your real inventory
5. Edit BANK_DETAILS with your account info
6. Run: python3 bot.py
7. Deploy free 24/7 on Render.com / Railway.app / a VPS (see notes at bottom)

ADMIN NOTIFICATIONS: every booking + payment screenshot is forwarded to your
ADMIN_CHAT_ID so you approve manually. To get your chat ID, message @userinfobot.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)

logging.basicConfig(level=logging.INFO)

# ============ CONFIG - EDIT THESE ============
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set this in Render's Environment tab, not here
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "123456789"))  # also set in Render

BANK_DETAILS = (
    "🏦 *Payment Details*\n\n"
    "Bank: [Your Bank Name]\n"
    "Account Name: Affirmative Group Holdings\n"
    "Account Number: [Your Account Number]\n\n"
    "Send your payment, then upload a screenshot here to confirm."
)

BILLBOARDS = [
    {
        "id": "bb1",
        "name": "96 Sheet Landscape Billboard, Sapele Rd by Ikpopan Junction",
        "location": "Sapele Road by Ikpopan Junction, Edo State",
        "price": 780000,  # 650,000 base + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/11/96-Sheet-Landscape-Billboard-Benin-Sapele-Road-By-Ikpopan-Junction-Edo-State-300x300.jpg",
    },
    {
        "id": "bb2",
        "name": "Gantry Billboard, New Benin Market FTF Uselu Share",
        "location": "New Benin Market, FTF Uselu Share, Edo State",
        "price": 1068000,  # 890,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Gantry-Billboard-New-Benin-Market-FTF-Uselu-Share-Edo-State-300x300.jpg",
    },
    {
        "id": "bb3",
        "name": "Gantry Billboard, New Lagos Road by New Benin Market",
        "location": "New Lagos Road by New Benin Market, Edo State",
        "price": 1920000,  # 1,600,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Gantry-Billboard-New-Lagos-Road-By-New-Benin-Market-Edo-State-300x300.jpg",
    },
    {
        "id": "bb4",
        "name": "Outdoor Unipole Billboard, University of Benin",
        "location": "University of Benin, Edo State",
        "price": 1080000,  # 900,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Outdoor-Unipole-Billboard-By-University-Of-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb5",
        "name": "Portrait Billboard, Ikpoba Hill by Ramat Park",
        "location": "Ikpoba Hill by Ramat Park, Edo State",
        "price": 900000,  # 750,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Advertising-Billboard-Ikpoba-Hill-By-Ramat-Park-Edo-State-300x300.jpg",
    },
    {
        "id": "bb6",
        "name": "Portrait Billboard, Siluko Road",
        "location": "Siluko Road, Benin City, Edo State",
        "price": 480000,  # 400,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Advertising-Billboard-Siluko-Road-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb7",
        "name": "Portrait Billboard, Mission Road by Unity Bank",
        "location": "Mission Road by Unity Bank, Benin City, Edo State",
        "price": 720000,  # 600,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Along-Mission-Road-By-Unity-Bank-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb8",
        "name": "Portrait Billboard, Benin-Abuja Road",
        "location": "Benin-Abuja Road, Edo State",
        "price": 420000,  # 350,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Benin-along-Abuja-Road-Edo-State-300x300.jpg",
    },
    {
        "id": "bb9",
        "name": "Portrait Billboard, Benin-Lagos Road by UNIBEN",
        "location": "Benin-Lagos Road by University of Benin, Edo State",
        "price": 900000,  # 750,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Benin-lagos-Road-By-Uni-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb10",
        "name": "Portrait Billboard, TV Road by 5 Junction Roundabout",
        "location": "TV Road by 5 Junction Roundabout, Edo State",
        "price": 420000,  # 350,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-TV-Road-By-5-Junction-Round-About-Edo-State-300x300.jpg",
    },
    {
        "id": "bb11",
        "name": "Unipole Billboard, Ekewan Road by University",
        "location": "Ekewan Road by University, Edo State",
        "price": 900000,  # 750,000 + 20%
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Unipole-Advertising-Billboard-Ekewan-Road-By-University-Edo-State-300x300.jpg",
    },
]
# Prices above are per booking period (typically monthly OOH rate) — adjust
# PERIOD_LABEL below to match how you actually want to sell (per week/month).
PERIOD_LABEL = "month"
# ==============================================

# Conversation states
CHOOSING_BOARD, CHOOSING_DURATION, ENTERING_DATES, ENTERING_CONTACT, AWAITING_PROOF = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 View Billboards", callback_data="view_boards")],
        [InlineKeyboardButton("💰 Pricing", callback_data="pricing")],
        [InlineKeyboardButton("📞 Talk to a Human", callback_data="human")],
    ]
    await update.message.reply_text(
        "👋 Welcome to *YUYU Ads*\nBillboard & LED screen bookings in Benin City.\n\n"
        "What would you like to do?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def view_boards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{b['name'][:35]} — ₦{b['price']:,}", callback_data=f"select_{b['id']}")]
        for b in BILLBOARDS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_start")])
    text = (
        f"📋 *Available Billboard Slots in Edo State*\n"
        f"Prices are per {PERIOD_LABEL}. Tap one to see photo, location & book:"
    )
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        # original message was a photo (no text to edit) — delete it and send fresh
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def select_board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board_id = query.data.replace("select_", "")
    board = next(b for b in BILLBOARDS if b["id"] == board_id)
    context.user_data["board"] = board

    keyboard = [
        [InlineKeyboardButton(f"✅ Book — ₦{board['price']:,}/{PERIOD_LABEL}", callback_data="confirm_board")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data="view_boards")],
    ]
    caption = (
        f"📍 *{board['name']}*\n"
        f"🗺️ {board['location']}\n"
        f"💵 ₦{board['price']:,} / {PERIOD_LABEL}\n\n"
        f"Tap below to proceed with booking."
    )
    try:
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=board["image"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        # remove the old text menu message to keep the chat clean
        await query.message.delete()
    except Exception:
        # fallback to text-only if image fails to load
        await query.edit_message_text(
            caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    return ENTERING_DATES


async def confirm_board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board = context.user_data["board"]
    total = board["price"]
    context.user_data["total"] = total

    await query.message.reply_text(
        f"✅ *{board['name']}* — 1 {PERIOD_LABEL}\n"
        f"💵 Total: ₦{total:,}\n\n"
        f"Please type your *full name and preferred start date* (e.g. 'John Okoro, starting 10th July').",
        parse_mode="Markdown"
    )
    return ENTERING_CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer_info"] = update.message.text
    board = context.user_data["board"]
    total = context.user_data["total"]

    await update.message.reply_text(
        f"Got it ✅\n\n{BANK_DETAILS}\n\n"
        f"💵 *Amount to pay: ₦{total:,}*\n\n"
        f"📸 Once paid, send a screenshot of your transfer here.",
        parse_mode="Markdown"
    )

    # notify admin of new booking request
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"🆕 *New Booking Request*\n"
        f"Board: {board['name']}\n"
        f"Location: {board['location']}\n"
        f"Total: ₦{total:,}\n"
        f"Customer: {context.user_data['customer_info']}\n"
        f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
        f"Awaiting payment screenshot.",
        parse_mode="Markdown"
    )
    return AWAITING_PROOF


async def receive_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = context.user_data.get("board", {})
    total = context.user_data.get("total", 0)
    customer_info = context.user_data.get("customer_info", "Unknown")

    # forward the screenshot to admin
    photo = update.message.photo[-1]
    await context.bot.send_photo(
        ADMIN_CHAT_ID,
        photo.file_id,
        caption=(
            f"💰 *Payment Screenshot Received*\n"
            f"Board: {board.get('name')}\n"
            f"Total: ₦{total:,}\n"
            f"Customer: {customer_info}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"✅ Reply here to confirm manually with the customer."
        ),
        parse_mode="Markdown"
    )
    await update.message.reply_text(
        "✅ Screenshot received! Your booking is *pending confirmation*.\n"
        "You'll hear from us within a few hours to confirm your slot.\n\n"
        "Thank you for choosing YUYU Ads 🙌",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"💰 *Current Pricing* (per {PERIOD_LABEL})\n\n" + "\n".join(
        f"• {b['name']}\n   {b['location']} — ₦{b['price']:,}" for b in BILLBOARDS
    )
    await query.edit_message_text(text, parse_mode="Markdown")


async def human(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 Reach us directly:\nWhatsApp: [your WhatsApp number]\nCall: [your phone number]"
    )


async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📋 View Billboards", callback_data="view_boards")],
        [InlineKeyboardButton("💰 Pricing", callback_data="pricing")],
        [InlineKeyboardButton("📞 Talk to a Human", callback_data="human")],
    ]
    await query.edit_message_text(
        "👋 Welcome back to *YUYU Ads*.\nWhat would you like to do?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Booking cancelled. Type /start to begin again.")
    return ConversationHandler.END


def main():
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_board, pattern="^select_")],
        states={
            ENTERING_DATES: [CallbackQueryHandler(confirm_board, pattern="^confirm_board$")],
            ENTERING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            AWAITING_PROOF: [MessageHandler(filters.PHOTO, receive_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(view_boards, pattern="^view_boards$"))
    app.add_handler(CallbackQueryHandler(pricing, pattern="^pricing$"))
    app.add_handler(CallbackQueryHandler(human, pattern="^human$"))
    app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start$"))
    app.add_handler(CallbackQueryHandler(select_board, pattern="^select_"))

    print("YUYU Ads bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

# ============================================
# FREE 24/7 DEPLOYMENT (so it runs when your phone is off):
# Option A - Render.com: create free "Background Worker", connect this file,
#            add BOT_TOKEN as environment variable, deploy.
# Option B - Railway.app: similar free-tier flow, deploy from GitHub repo.
# Option C - Termux on your Redmi phone: run it directly on-device 24/7
#            if the phone stays on and connected (least reliable but zero cost).
# ============================================
