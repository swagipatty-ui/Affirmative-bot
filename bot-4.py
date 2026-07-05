"""
AFFIRMATIVE CRAFT PACKAGING - Telegram Bot
Services: Packaging | Printing | Advertisement | Exchange

SETUP:
1. pip install python-telegram-bot --break-system-packages --upgrade
2. Get a bot token from @BotFather
3. export BOT_TOKEN="..." and export ADMIN_CHAT_ID="..." before running
4. Edit CATALOG below to adjust items/prices/images any time
5. Run: python3 bot.py

ADMIN NOTIFICATIONS: every order request + payment screenshot + exchange
request is forwarded to ADMIN_CHAT_ID for manual confirmation.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)

logging.basicConfig(level=logging.INFO)

# ============ CONFIG ============
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))

BANK_DETAILS = (
    "🏦 *Payment Details*\n\n"
    "Bank: [United bank of Africa]\n"
    "Account Name: young yuyu ukhuegbe \n"
    "Account Number: [2136061133]\n\n"
    "Send your payment, then upload a screenshot here to confirm."
)

# Front page banner shown after /start — put affirmative_banner.jpg in the
# same folder as bot.py (same repo/directory) to use your own image.
WELCOME_IMAGE = "affirmative_banner.jpg"

WELCOME_TEXT = (
    "✨ *Welcome to Affirmative Craft Packaging* ✨\n\n"
    "_Print it. Brand it. Flaunt it._\n\n"
    "From premium packaging and print production, to outdoor advertising "
    "and secure currency exchange — we bring your business to life across "
    "every channel.\n\n"
    "Please choose a service below to get started:"
)

# ============ CATALOG ============
# Structure: SERVICES -> CATEGORIES -> ITEMS
# Prices marked "placeholder est." are estimates - update with real costs.

CATALOG_CATEGORIES = {
    "pkg_bags": {
        "label": "Paper Bags 🛍️",
        "cover_image": "images/pkg_paperbag_longchamp.jpg",
        "items": [
            {
                "id": "pb1",
                "name": "X-Large Paper Bag (A2 Landscape)",
                "price": 680,
                "moq": 100,
                "image": "https://inklets.com.ng/wp-content/uploads/2024/09/x-large-paper-bag.jpg",
                "note": "Full colour branding, rope handles (placeholder est.)",
            },
            {
                "id": "pb2",
                "name": "Christmas Themed Gift Bag (Twisted Handle)",
                "price": 405,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/christmas-gift-bag.jpg",
                "note": "Seasonal print, twisted paper handle",
            },
            {
                "id": "pb3",
                "name": "Good Time Kraft (Brown) Gift Bag, Rope Handle",
                "price": 360,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/kraft-gift-bag.jpg",
                "note": "Natural kraft finish, rope handles",
            },
            {
                "id": "pb4",
                "name": "Healthy Food Kraft Bag",
                "price": 360,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/healthy-food-bag.jpg",
                "note": "Food-safe kraft, printed design",
            },
        ],
    },
    "pkg_nylon": {
        "label": "Nylon Bags (Ziplock & Mailer) 🛍️",
        "cover_image": "images/pkg_ziplock_zevora.jpg",
        "items": [
            {
                "id": "nb1",
                "name": "Ziplock Nylon Bag (Frosted, Custom Print)",
                "price": 315,
                "moq": 50,
                "image": "images/pkg_ziplock_luxe.jpg",
                "note": "Resealable zip closure, full colour branding (placeholder est.)",
            },
            {
                "id": "nb2",
                "name": "Ziplock Nylon Bag (Clear/Grey, Custom Print)",
                "price": 315,
                "moq": 50,
                "image": "images/pkg_ziplock_elexio.jpg",
                "note": "Premium matte finish (placeholder est.)",
            },
            {
                "id": "nb3",
                "name": "Ziplock Nylon Bag (Glossy Transparent Tote Style)",
                "price": 360,
                "moq": 50,
                "image": "images/pkg_ziplock_pinqpolka.jpg",
                "note": "Bold colour PVC, sturdy handles (placeholder est.)",
            },
            {
                "id": "nb4",
                "name": "Courier Mailer Bag (Matte, Custom Print)",
                "price": 270,
                "moq": 100,
                "image": "images/pkg_mailer_lissen.jpg",
                "note": "Tamper-evident seal, waterproof (placeholder est.)",
            },
            {
                "id": "nb5",
                "name": "Courier Mailer Bag (Glossy, Custom Print)",
                "price": 270,
                "moq": 100,
                "image": "images/pkg_mailer_muchlove.jpg",
                "note": "Water-resistant, tear-proof (placeholder est.)",
            },
            {
                "id": "nb6",
                "name": "Kraft-Style Mailer Bag with Drawstring",
                "price": 495,
                "moq": 50,
                "image": "images/pkg_mailer_booandco.jpg",
                "note": "Eco kraft finish, drawstring close (placeholder est.)",
            },
        ],
    },
    "pkg_labels": {
        "label": "Labels & Stickers 🏷️",
        "cover_image": None,
        "items": [
            {
                "id": "lb1",
                "name": "Custom Product Labels (Roll of 500)",
                "price": 13500,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/label-roll.jpg",
                "note": "Waterproof vinyl, full colour (placeholder est.)",
            },
            {
                "id": "lb2",
                "name": "Branded Sticker Sheets (A4, pack of 50)",
                "price": 9000,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/sticker-sheet.jpg",
                "note": "Glossy or matte finish (placeholder est.)",
            },
        ],
    },
    "pkg_boxes": {
        "label": "Boxes 🎁",
        "cover_image": "images/pkg_box_mundosetti.jpg",
        "items": [
            {
                "id": "bx1",
                "name": "White Gable Box",
                "price": 315,
                "moq": 50,
                "image": "https://packhub.ng/wp-content/uploads/white-gable-box.jpg",
                "note": "Grease-resistant, customizable branding (placeholder est.)",
            },
            {
                "id": "bx2",
                "name": "Corrugated Kraft (Brown) Large Box",
                "price": 450,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/kraft-large-box.jpg",
                "note": "Recycled carton, sturdy for logistics (placeholder est.)",
            },
            {
                "id": "bx3",
                "name": "Bagasse Bento Cake Box",
                "price": 315,
                "moq": 50,
                "image": "https://packhub.ng/wp-content/uploads/bento-cake-box.jpg",
                "note": "Eco-friendly, leak resistant",
            },
        ],
    },
    "pkg_books": {
        "label": "Books & Jotters 📚",
        "cover_image": None,
        "items": [
            {
                "id": "bk1",
                "name": "Branded A5 Jotter (100 pages)",
                "price": 675,
                "moq": 50,
                "image": "https://inklets.com.ng/wp-content/uploads/jotter.jpg",
                "note": "Custom cover print, spiral or perfect bound (placeholder est.)",
            },
        ],
    },
    "pkg_plastic": {
        "label": "Plastic Packs 🧴",
        "cover_image": "images/pkg_ziplock_pinqpolka.jpg",
        "items": [
            {
                "id": "pl1",
                "name": "Branded Poly Bags (pack of 100)",
                "price": 4500,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/poly-bag.jpg",
                "note": "Tamper-evident, custom print (placeholder est.)",
            },
        ],
    },
    "prt_banners": {
        "label": "Banners 🖼️",
        "cover_image": None,
        "items": [
            {
                "id": "bn1",
                "name": "Roll-Up Banner (85x200cm)",
                "price": 13500,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/rollup-banner.jpg",
                "note": "Includes stand, full colour print (placeholder est.)",
            },
        ],
    },
    "prt_stickers": {
        "label": "SAV Stickers 🏷️",
        "cover_image": None,
        "items": [
            {
                "id": "sv1",
                "name": "SAV Vinyl Sticker (per sqm)",
                "price": 4050,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/sav-sticker.jpg",
                "note": "Outdoor durable, custom cut (placeholder est.)",
            },
        ],
    },
    "prt_shirts": {
        "label": "Shirts 👕",
        "cover_image": None,
        "items": [
            {
                "id": "sh1",
                "name": "Branded Round Neck T-Shirt",
                "price": 4500,
                "moq": 20,
                "image": "https://inklets.com.ng/wp-content/uploads/round-neck-tshirt.jpg",
                "note": "100% cotton, custom print/embroidery (placeholder est.)",
            },
        ],
    },
    "prt_caps": {
        "label": "Caps 🧢",
        "cover_image": None,
        "items": [
            {
                "id": "cp1",
                "name": "Branded Face Cap",
                "price": 3150,
                "moq": 20,
                "image": "https://inklets.com.ng/wp-content/uploads/face-cap.jpg",
                "note": "Embroidered or printed logo (placeholder est.)",
            },
        ],
    },
    "prt_pens": {
        "label": "Biro Pens 🖊️",
        "cover_image": None,
        "items": [
            {
                "id": "bp1",
                "name": "Branded Biro Pen (box of 50)",
                "price": 9000,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/biro-pen.jpg",
                "note": "Custom logo print (placeholder est.)",
            },
        ],
    },
    "prt_mugs": {
        "label": "Mock Cups / Mugs 🍵",
        "cover_image": None,
        "items": [
            {
                "id": "mg1",
                "name": "Branded Ceramic Mug",
                "price": 2700,
                "moq": 20,
                "image": "https://inklets.com.ng/wp-content/uploads/branded-mug.jpg",
                "note": "Dishwasher-safe print (placeholder est.)",
            },
        ],
    },
    "prt_aprons": {
        "label": "Aprons 🥻",
        "cover_image": None,
        "items": [
            {
                "id": "ap1",
                "name": "Branded Kitchen Apron",
                "price": 3600,
                "moq": 10,
                "image": "https://inklets.com.ng/wp-content/uploads/apron.jpg",
                "note": "Durable fabric, logo print (placeholder est.)",
            },
        ],
    },
}

# Real Edo State billboard listings (source: Alternative Adverts), +20% markup applied
BILLBOARDS = [
    {
        "id": "bb1",
        "name": "96 Sheet Landscape Billboard, Sapele Rd by Ikpopan Junction",
        "location": "Sapele Road by Ikpopan Junction, Edo State",
        "price": 780000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/11/96-Sheet-Landscape-Billboard-Benin-Sapele-Road-By-Ikpopan-Junction-Edo-State-300x300.jpg",
    },
    {
        "id": "bb2",
        "name": "Gantry Billboard, New Benin Market FTF Uselu Share",
        "location": "New Benin Market, FTF Uselu Share, Edo State",
        "price": 1068000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Gantry-Billboard-New-Benin-Market-FTF-Uselu-Share-Edo-State-300x300.jpg",
    },
    {
        "id": "bb3",
        "name": "Gantry Billboard, New Lagos Road by New Benin Market",
        "location": "New Lagos Road by New Benin Market, Edo State",
        "price": 1920000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Gantry-Billboard-New-Lagos-Road-By-New-Benin-Market-Edo-State-300x300.jpg",
    },
    {
        "id": "bb4",
        "name": "Outdoor Unipole Billboard, University of Benin",
        "location": "University of Benin, Edo State",
        "price": 1080000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Outdoor-Unipole-Billboard-By-University-Of-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb5",
        "name": "Portrait Billboard, Ikpoba Hill by Ramat Park",
        "location": "Ikpoba Hill by Ramat Park, Edo State",
        "price": 900000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Advertising-Billboard-Ikpoba-Hill-By-Ramat-Park-Edo-State-300x300.jpg",
    },
    {
        "id": "bb6",
        "name": "Portrait Billboard, Siluko Road",
        "location": "Siluko Road, Benin City, Edo State",
        "price": 480000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Advertising-Billboard-Siluko-Road-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb7",
        "name": "Portrait Billboard, Mission Road by Unity Bank",
        "location": "Mission Road by Unity Bank, Benin City, Edo State",
        "price": 720000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Along-Mission-Road-By-Unity-Bank-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb8",
        "name": "Portrait Billboard, Benin-Abuja Road",
        "location": "Benin-Abuja Road, Edo State",
        "price": 420000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Benin-along-Abuja-Road-Edo-State-300x300.jpg",
    },
    {
        "id": "bb9",
        "name": "Portrait Billboard, Benin-Lagos Road by UNIBEN",
        "location": "Benin-Lagos Road by University of Benin, Edo State",
        "price": 900000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Benin-lagos-Road-By-Uni-Benin-Edo-State-300x300.jpg",
    },
    {
        "id": "bb10",
        "name": "Portrait Billboard, TV Road by 5 Junction Roundabout",
        "location": "TV Road by 5 Junction Roundabout, Edo State",
        "price": 420000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-TV-Road-By-5-Junction-Round-About-Edo-State-300x300.jpg",
    },
    {
        "id": "bb11",
        "name": "Unipole Billboard, Ekewan Road by University",
        "location": "Ekewan Road by University, Edo State",
        "price": 900000,
        "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Unipole-Advertising-Billboard-Ekewan-Road-By-University-Edo-State-300x300.jpg",
    },
]
BILLBOARD_PERIOD = "month"

EXCHANGE_ASSETS = ["USDT", "RMB", "SOL", "BTC", "ETH"]

# Real influencers from Mysogi (mysogi.com.ng), only those with visible
# per-post pricing, +15% markup applied to the base price shown.
INFLUENCERS = [
    {"id": "inf1", "name": "Mr Alabi", "role": "Influencer", "followers": 325000, "price": 69000},
    {"id": "inf2", "name": "ElegantSlayers", "role": "Blogger", "followers": 366000, "price": 57500},
    {"id": "inf3", "name": "Futagrammm", "role": "Blogger", "followers": 108000, "price": 34500},
    {"id": "inf4", "name": "Kythegod", "role": "Influencer", "followers": 40000, "price": 34500},
    {"id": "inf5", "name": "Campus Hubb", "role": "Blogger", "followers": 22000, "price": 11500},
    {"id": "inf6", "name": "Legalnaija", "role": "Blogger", "followers": 19300, "price": 23000},
    {"id": "inf7", "name": "Egbamitv", "role": "Influencer", "followers": 34000, "price": 34500},
    {"id": "inf8", "name": "The CU Student", "role": "Influencer", "followers": 184000, "price": 5750},
    {"id": "inf9", "name": "Nkecci", "role": "Influencer", "followers": 37500, "price": 92000},
    {"id": "inf10", "name": "Ari Debby", "role": "Influencer", "followers": 86000, "price": 172500},
]

# WhatsApp Marketing - Nigerian marketplace group posting tiers
WHATSAPP_TIERS = [
    {"id": "wa1", "label": "50 groups post", "price": 5000},
    {"id": "wa2", "label": "100 buy & selling groups post", "price": 10000},
    {"id": "wa3", "label": "250 groups post", "price": 22000},
    {"id": "wa4", "label": "500 super active marketplace groups post", "price": 48000},
    {"id": "wa5", "label": "1000 super active marketplace buy & sell groups post", "price": 100000},
]

ONLINE_AD_PLATFORMS = {
    "oa_influencer": {"label": "Influencer Ads/Post 🤳", "logo": "📸"},
    "oa_whatsapp": {"label": "WhatsApp Marketing 💬", "logo": "💬"},
    "oa_instagram": {"label": "Instagram UGC Ads 📷", "logo": "📷"},
    "oa_snapchat": {"label": "Snapchat Ads 👻", "logo": "👻"},
    "oa_facebook": {"label": "Facebook Ads 📘", "logo": "📘"},
    "oa_tiktok": {"label": "TikTok Ads 🎵", "logo": "🎵"},
}

# ============ CONVERSATION STATES ============
(
    AWAITING_ORDER_QTY,
    AWAITING_ORDER_CONTACT,
    AWAITING_ORDER_PROOF,
    AWAITING_BILLBOARD_CONTACT,
    AWAITING_BILLBOARD_PROOF,
    AWAITING_EXCHANGE_AMOUNT,
    AWAITING_EXCHANGE_CONTACT,
    AWAITING_INFLUENCER_CONTACT,
    AWAITING_WHATSAPP_CONTACT,
) = range(9)


# ============ HELPERS ============
def find_item(category_dict, item_id):
    for cat in category_dict.values():
        for item in cat["items"]:
            if item["id"] == item_id:
                return item
    return None


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦🖨️ Packaging & Printing", callback_data="svc_catalog")],
        [InlineKeyboardButton("📢 Advertisement", callback_data="svc_advertisement")],
        [InlineKeyboardButton("💱 Exchange", callback_data="svc_exchange")],
    ])


# ============ START / MAIN MENU ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as img:
                await update.message.reply_photo(
                    photo=img,
                    caption=WELCOME_TEXT,
                    reply_markup=main_menu_keyboard(),
                    parse_mode="Markdown"
                )
                return
    except Exception:
        pass
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="Markdown"
        )
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=WELCOME_TEXT,
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )


# ============ PACKAGING & PRINTING (shared logic) ============
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(cat["label"], callback_data=f"cat_{key}")]
        for key, cat in CATALOG_CATEGORIES.items()
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")])

    text = "📦🖨️ *Packaging & Printing*\n\nChoose a category:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_key = query.data.replace("cat_", "")
    category = CATALOG_CATEGORIES[cat_key]
    context.user_data["cat_key"] = cat_key

    keyboard = [
        [InlineKeyboardButton(f"{item['name'][:35]} — ₦{item['price']:,}", callback_data=f"item_{item['id']}")]
        for item in category["items"]
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="svc_catalog")])
    text = f"*{category['label']}*\n\nTap an item to view details & order:"

    cover = category.get("cover_image")
    if cover and os.path.exists(cover):
        try:
            await query.message.delete()
        except Exception:
            pass
        with open(cover, "rb") as img:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img,
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        return

    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_item_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item_id = query.data.replace("item_", "")
    item = find_item(CATALOG_CATEGORIES, item_id)
    context.user_data["item"] = item

    caption = (
        f"*{item['name']}*\n"
        f"💵 ₦{item['price']:,} per unit\n"
        f"📦 MOQ: {item['moq']} units\n"
        f"📝 {item['note']}\n\n"
        f"Tap below to order."
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Order This", callback_data="order_item")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data=f"cat_{context.user_data.get('cat_key')}")],
    ]
    image_path = item["image"]
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=img,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
        else:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=image_path,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        await query.message.delete()
    except Exception:
        try:
            await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception:
            await context.bot.send_message(
                chat_id=query.message.chat_id, text=caption,
                reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )


async def order_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = context.user_data["item"]
    await query.message.reply_text(
        f"How many units of *{item['name']}* would you like? (minimum {item['moq']})",
        parse_mode="Markdown"
    )
    return AWAITING_ORDER_QTY


async def order_item_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = context.user_data["item"]
    try:
        qty = int("".join(ch for ch in update.message.text if ch.isdigit()))
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return AWAITING_ORDER_QTY

    if qty < item["moq"]:
        await update.message.reply_text(
            f"⚠️ Minimum order quantity is {item['moq']}. Please enter {item['moq']} or more."
        )
        return AWAITING_ORDER_QTY

    total = qty * item["price"]
    context.user_data["qty"] = qty
    context.user_data["total"] = total

    await update.message.reply_text(
        f"✅ *{item['name']}* x {qty}\n💵 Total: ₦{total:,}\n\n"
        f"Please type your *full name and delivery address*.",
        parse_mode="Markdown"
    )
    return AWAITING_ORDER_CONTACT


async def order_item_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer_info"] = update.message.text
    item = context.user_data["item"]
    total = context.user_data["total"]
    qty = context.user_data["qty"]

    await update.message.reply_text(
        f"Got it ✅\n\n{BANK_DETAILS}\n\n💵 *Amount to pay: ₦{total:,}*\n\n"
        f"📸 Once paid, send a screenshot of your transfer here.",
        parse_mode="Markdown"
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *New Order*\n"
            f"Item: {item['name']}\n"
            f"Qty: {qty}\n"
            f"Total: ₦{total:,}\n"
            f"Customer: {context.user_data['customer_info']}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"Awaiting payment screenshot.",
            parse_mode="Markdown"
        )
    return AWAITING_ORDER_PROOF


async def order_item_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = context.user_data.get("item", {})
    total = context.user_data.get("total", 0)
    qty = context.user_data.get("qty", 0)
    customer_info = context.user_data.get("customer_info", "Unknown")

    photo = update.message.photo[-1]
    if ADMIN_CHAT_ID:
        await context.bot.send_photo(
            ADMIN_CHAT_ID,
            photo.file_id,
            caption=(
                f"💰 *Payment Screenshot Received*\n"
                f"Item: {item.get('name')}\n"
                f"Qty: {qty}\n"
                f"Total: ₦{total:,}\n"
                f"Customer: {customer_info}\n"
                f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
                f"✅ Reply here to confirm manually with the customer."
            ),
            parse_mode="Markdown"
        )
    await update.message.reply_text(
        "✅ Screenshot received! Your order is *pending confirmation*.\n"
        "You'll hear from us shortly.\n\nThank you for choosing Affirmative Group Holdings 🙌",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ============ ADVERTISEMENT ============
async def show_ad_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛣️ Outdoor Billboard", callback_data="ad_outdoor")],
        [InlineKeyboardButton("💻 Online Advertisement", callback_data="ad_online")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")],
    ]
    text = "📢 *Advertisement Services*\n\nChoose a channel:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_online_ad_platforms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(p["label"], callback_data=key)]
        for key, p in ONLINE_AD_PLATFORMS.items()
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="svc_advertisement")])
    text = "💻 *Online Advertisement*\n\nChoose a platform:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_influencer_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{inf['name']} ({inf['followers']:,}) — ₦{inf['price']:,}", callback_data=f"inf_{inf['id']}")]
        for inf in INFLUENCERS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="ad_online")])
    text = "📸 *Influencer Ads/Post*\n\nReal verified creators — tap one to view details and book:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_influencer_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inf_id = query.data.replace("inf_", "")
    inf = next(i for i in INFLUENCERS if i["id"] == inf_id)
    context.user_data["influencer"] = inf

    text = (
        f"📸 *{inf['name']}*\n"
        f"Role: {inf['role']}\n"
        f"Followers: {inf['followers']:,}\n"
        f"💵 ₦{inf['price']:,} per post\n\n"
        f"Tap below to book this influencer."
    )
    keyboard = [
        [InlineKeyboardButton(f"✅ Book — ₦{inf['price']:,}", callback_data="confirm_influencer")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data="oa_influencer")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def confirm_influencer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inf = context.user_data["influencer"]
    context.user_data["total"] = inf["price"]
    await query.message.reply_text(
        f"✅ *{inf['name']}* — 1 post\n💵 Total: ₦{inf['price']:,}\n\n"
        f"Please share your *brand name, product/service, and what you'd like posted*.",
        parse_mode="Markdown"
    )
    return AWAITING_INFLUENCER_CONTACT


async def influencer_contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_info = update.message.text
    inf = context.user_data.get("influencer", {})
    total = context.user_data.get("total", 0)

    await update.message.reply_text(
        f"Got it ✅\n\n{BANK_DETAILS}\n\n💵 *Amount to pay: ₦{total:,}*\n\n"
        f"📸 Once paid, send a screenshot of your transfer here.",
        parse_mode="Markdown"
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *New Influencer Booking*\n"
            f"Influencer: {inf.get('name')}\n"
            f"Total: ₦{total:,}\n"
            f"Brief: {contact_info}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"Awaiting payment screenshot.",
            parse_mode="Markdown"
        )
    return AWAITING_ORDER_PROOF


async def show_whatsapp_tiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{t['label']} — ₦{t['price']:,}", callback_data=f"wa_{t['id']}")]
        for t in WHATSAPP_TIERS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="ad_online")])
    text = (
        "💬 *WhatsApp Marketing*\n\n"
        "Post your ad across active Nigerian WhatsApp buy & sell marketplace groups "
        "spanning all 36 states. Choose a package:"
    )
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def confirm_whatsapp_tier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tier_id = query.data.replace("wa_", "")
    tier = next(t for t in WHATSAPP_TIERS if t["id"] == tier_id)
    context.user_data["wa_tier"] = tier
    context.user_data["total"] = tier["price"]

    await query.message.reply_text(
        f"✅ *{tier['label']}*\n💵 Total: ₦{tier['price']:,}\n\n"
        f"Please share the *ad text/content* you'd like posted, plus your contact info.",
        parse_mode="Markdown"
    )
    return AWAITING_WHATSAPP_CONTACT


async def whatsapp_contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_info = update.message.text
    tier = context.user_data.get("wa_tier", {})
    total = context.user_data.get("total", 0)

    await update.message.reply_text(
        f"Got it ✅\n\n{BANK_DETAILS}\n\n💵 *Amount to pay: ₦{total:,}*\n\n"
        f"📸 Once paid, send a screenshot of your transfer here.",
        parse_mode="Markdown"
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *New WhatsApp Marketing Order*\n"
            f"Package: {tier.get('label')}\n"
            f"Total: ₦{total:,}\n"
            f"Ad content/contact: {contact_info}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"Awaiting payment screenshot.",
            parse_mode="Markdown"
        )
    return AWAITING_ORDER_PROOF


async def show_platform_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    platform_key = query.data
    platform = ONLINE_AD_PLATFORMS[platform_key]
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="ad_online")]]
    await query.edit_message_text(
        f"{platform['logo']} *{platform['label']}*\n\n"
        f"We run targeted campaigns on this platform tailored to your budget and goals. "
        f"Message us directly to discuss your campaign:\n\n"
        f"WhatsApp: [your WhatsApp number]",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def show_billboards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{b['name'][:35]} — ₦{b['price']:,}", callback_data=f"bb_{b['id']}")]
        for b in BILLBOARDS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="svc_advertisement")])
    text = (
        f"🛣️ *Available Billboard Slots in Edo State*\n"
        f"Prices are per {BILLBOARD_PERIOD}. Tap one to see photo, location & book:"
    )
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_billboard_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board_id = query.data.replace("bb_", "")
    board = next(b for b in BILLBOARDS if b["id"] == board_id)
    context.user_data["board"] = board

    caption = (
        f"📍 *{board['name']}*\n"
        f"🗺️ {board['location']}\n"
        f"💵 ₦{board['price']:,} / {BILLBOARD_PERIOD}\n\n"
        f"Tap below to book."
    )
    keyboard = [
        [InlineKeyboardButton(f"✅ Book — ₦{board['price']:,}", callback_data="confirm_billboard")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data="ad_outdoor")],
    ]
    try:
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=board["image"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        await query.message.delete()
    except Exception:
        await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def confirm_billboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board = context.user_data["board"]
    context.user_data["total"] = board["price"]
    await query.message.reply_text(
        f"✅ *{board['name']}* — 1 {BILLBOARD_PERIOD}\n"
        f"💵 Total: ₦{board['price']:,}\n\n"
        f"Please type your *full name and preferred start date*.",
        parse_mode="Markdown"
    )
    return AWAITING_BILLBOARD_CONTACT


async def billboard_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer_info"] = update.message.text
    board = context.user_data["board"]
    total = context.user_data["total"]

    await update.message.reply_text(
        f"Got it ✅\n\n{BANK_DETAILS}\n\n💵 *Amount to pay: ₦{total:,}*\n\n"
        f"📸 Once paid, send a screenshot of your transfer here.",
        parse_mode="Markdown"
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *New Billboard Booking*\n"
            f"Board: {board['name']}\n"
            f"Location: {board['location']}\n"
            f"Total: ₦{total:,}\n"
            f"Customer: {context.user_data['customer_info']}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"Awaiting payment screenshot.",
            parse_mode="Markdown"
        )
    return AWAITING_BILLBOARD_PROOF


async def billboard_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = context.user_data.get("board", {})
    total = context.user_data.get("total", 0)
    customer_info = context.user_data.get("customer_info", "Unknown")

    photo = update.message.photo[-1]
    if ADMIN_CHAT_ID:
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
        "You'll hear from us within a few hours.\n\nThank you for choosing Affirmative Group Holdings 🙌",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ============ EXCHANGE ============
async def show_exchange_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("💵 Buy", callback_data="ex_buy"),
         InlineKeyboardButton("💴 Sell", callback_data="ex_sell")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")],
    ]
    text = "💱 *Currency & Crypto Exchange*\n\nWhat would you like to do?"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=text,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_exchange_assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.replace("ex_", "")
    context.user_data["ex_action"] = action

    keyboard = [
        [InlineKeyboardButton(asset, callback_data=f"exasset_{asset}")]
        for asset in EXCHANGE_ASSETS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="svc_exchange")])
    verb = "buy" if action == "buy" else "sell"
    await query.edit_message_text(
        f"What do you want to {verb}?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def exchange_ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    asset = query.data.replace("exasset_", "")
    context.user_data["ex_asset"] = asset
    action = context.user_data.get("ex_action", "buy")

    await query.edit_message_text(
        f"How much {asset} would you like to {action}? "
        f"(enter the amount, e.g. '500' or '0.05')",
        parse_mode="Markdown"
    )
    return AWAITING_EXCHANGE_AMOUNT


async def exchange_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ex_amount"] = update.message.text
    await update.message.reply_text(
        "Please share your *full name and phone number* so our team can reach you "
        "with the current rate and complete the transaction.",
        parse_mode="Markdown"
    )
    return AWAITING_EXCHANGE_CONTACT


async def exchange_contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_info = update.message.text
    action = context.user_data.get("ex_action", "buy")
    asset = context.user_data.get("ex_asset", "?")
    amount = context.user_data.get("ex_amount", "?")

    await update.message.reply_text(
        "✅ Request received! Our team will contact you shortly with the current "
        "rate to complete your transaction.\n\nThank you for choosing Affirmative Group Holdings 🙌",
        parse_mode="Markdown"
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"💱 *New Exchange Request*\n"
            f"Action: {action.upper()}\n"
            f"Asset: {asset}\n"
            f"Amount: {amount}\n"
            f"Customer: {contact_info}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"⚠️ Reply directly to the customer with your rate to proceed.",
            parse_mode="Markdown"
        )
    return ConversationHandler.END


# ============ MISC ============
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Type /start to begin again.")
    return ConversationHandler.END


def main():
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_item_start, pattern="^order_item$")],
        states={
            AWAITING_ORDER_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_item_qty)],
            AWAITING_ORDER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_item_contact)],
            AWAITING_ORDER_PROOF: [MessageHandler(filters.PHOTO, order_item_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    billboard_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(confirm_billboard, pattern="^confirm_billboard$")],
        states={
            AWAITING_BILLBOARD_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, billboard_contact)],
            AWAITING_BILLBOARD_PROOF: [MessageHandler(filters.PHOTO, billboard_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    exchange_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(exchange_ask_amount, pattern="^exasset_")],
        states={
            AWAITING_EXCHANGE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, exchange_amount_received)],
            AWAITING_EXCHANGE_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, exchange_contact_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    influencer_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(confirm_influencer, pattern="^confirm_influencer$")],
        states={
            AWAITING_INFLUENCER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, influencer_contact_received)],
            AWAITING_ORDER_PROOF: [MessageHandler(filters.PHOTO, order_item_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    whatsapp_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(confirm_whatsapp_tier, pattern="^wa_")],
        states={
            AWAITING_WHATSAPP_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, whatsapp_contact_received)],
            AWAITING_ORDER_PROOF: [MessageHandler(filters.PHOTO, order_item_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(order_conv)
    app.add_handler(billboard_conv)
    app.add_handler(exchange_conv)
    app.add_handler(influencer_conv)
    app.add_handler(whatsapp_conv)

    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^svc_catalog$"))
    app.add_handler(CallbackQueryHandler(show_ad_options, pattern="^svc_advertisement$"))
    app.add_handler(CallbackQueryHandler(show_exchange_options, pattern="^svc_exchange$"))
    app.add_handler(CallbackQueryHandler(show_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_item_detail, pattern="^item_"))
    app.add_handler(CallbackQueryHandler(show_billboards, pattern="^ad_outdoor$"))
    app.add_handler(CallbackQueryHandler(show_online_ad_platforms, pattern="^ad_online$"))
    app.add_handler(CallbackQueryHandler(show_billboard_detail, pattern="^bb_"))
    app.add_handler(CallbackQueryHandler(show_exchange_assets, pattern="^ex_(buy|sell)$"))
    app.add_handler(CallbackQueryHandler(show_influencer_list, pattern="^oa_influencer$"))
    app.add_handler(CallbackQueryHandler(show_influencer_detail, pattern="^inf_"))
    app.add_handler(CallbackQueryHandler(show_whatsapp_tiers, pattern="^oa_whatsapp$"))
    app.add_handler(CallbackQueryHandler(
        show_platform_info, pattern="^oa_(instagram|snapchat|facebook|tiktok)$"
    ))

    print("Affirmative Group Holdings bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

# ============================================
# NOTES
# - Prices marked "placeholder est." are estimates since exact per-unit
#   pricing wasn't publicly exposed on the source sites (variant-based
#   pricing shown only after selecting options on-page). Update these
#   directly in the CATALOG dictionaries above once you confirm real costs.
# - To use your own front-page image: upload affirmative_banner.jpg into
#   the same folder as bot.py (in your GitHub repo / Termux folder).
# - Exchange flow only collects the request; you manually reply with rates
#   via Telegram to close the transaction, exactly as you specified.
# ============================================
