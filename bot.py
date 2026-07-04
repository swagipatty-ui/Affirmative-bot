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
    {"id": "bb1", "name": "Ring Road Billboard (48-sheet)", "location": "Ring Road, Benin City", "price_weekly": 45000},
    {"id": "bb2", "name": "Sapele Road LED Screen", "location": "Sapele Road, Benin City", "price_weekly": 60000},
    {"id": "bb3", "name": "Airport Road Billboard", "location": "Airport Road, Benin City", "price_weekly": 40000},
]
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
        [InlineKeyboardButton(f"{b['name']} - ₦{b['price_weekly']:,}/wk", callback_data=f"select_{b['id']}")]
        for b in BILLBOARDS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_start")])
    await query.edit_message_text(
        "📋 *Available Slots*\nTap one to book:",
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
        [InlineKeyboardButton("1 Week", callback_data="dur_1"),
         InlineKeyboardButton("2 Weeks", callback_data="dur_2")],
        [InlineKeyboardButton("1 Month", callback_data="dur_4")],
        [InlineKeyboardButton("⬅️ Back", callback_data="view_boards")],
    ]
    await query.edit_message_text(
        f"📍 *{board['name']}*\n{board['location']}\n₦{board['price_weekly']:,}/week\n\n"
        f"How many weeks do you want to book?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ENTERING_DATES


async def select_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    weeks = int(query.data.replace("dur_", ""))
    board = context.user_data["board"]
    total = board["price_weekly"] * weeks
    context.user_data["weeks"] = weeks
    context.user_data["total"] = total

    await query.edit_message_text(
        f"✅ *{board['name']}* — {weeks} week(s)\n"
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
        f"Duration: {context.user_data['weeks']} week(s)\n"
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
    text = "💰 *Current Pricing*\n\n" + "\n".join(
        f"• {b['name']} — ₦{b['price_weekly']:,}/week" for b in BILLBOARDS
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
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_board, pattern="^select_")],
        states={
            ENTERING_DATES: [CallbackQueryHandler(select_duration, pattern="^dur_")],
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
