"""
AFFIRMATIVE GROUP HOLDINGS - Telegram Bot
Services: Packaging | Printing | Advertisement | Exchange

WHAT'S NEW IN THIS VERSION:
- Onboarding: asks gender first, then name, then phone number.
  Every message afterward greets them personally (time-of-day + Mummy/Ma/Madam
  or Sir/Daddy/Oga depending on gender) and uses their name in key moments.
- Every product now has short, warm hype copy when tapped, plus its image.
- Packaging > Paper Bags now has a "Nylon & Mailer Bags" sub-style gallery
  (Elexio/Malika Modesty/Luxe/Zevora/Lissen-style matte ziplock + mailer looks)
  as an aesthetic front page before showing real orderable products.
- Advertisement > Online Advertisement is fully rebuilt:
    Influencer Ads/Posts -> real influencer roster (name, followers, price+10%)
    WhatsApp Marketing    -> Nigerian WhatsApp marketplace group tiers
    Instagram UGC / Snapchat / Facebook / TikTok ads -> platform info + contact
- Every customer's name, phone, gender, and requests are appended to
  customers.csv in this same folder, so you can open it in Excel/Sheets later.

SETUP:
1. pip install python-telegram-bot --break-system-packages --upgrade
2. Get a bot token from @BotFather
3. export BOT_TOKEN="..." and export ADMIN_CHAT_ID="..." before running
4. Put affirmative_banner.png (front page image) in this same folder.
5. Run: python3 bot.py

PRICING NOTE: Packaging/Printing prices are the real listed prices from
Inklets/PackHub minus 10%. Influencer prices are Mysogi's listed per-post
rate plus 10% (as requested — a markup, not a discount, on this category).
Update numbers directly in this file any time source prices change.
"""

import os
import csv
import logging
from datetime import datetime, timezone, timedelta

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
    "Bank: [Your Bank Name]\n"
    "Account Name: Affirmative Group Holdings\n"
    "Account Number: [Your Account Number]\n\n"
    "Send your payment, then upload a screenshot here to confirm."
)

WELCOME_IMAGE = "affirmative_banner.png"
CUSTOMERS_FILE = "customers.csv"
NG_TZ = timezone(timedelta(hours=1))  # WAT

# ============ PERSONALIZATION HELPERS ============

def time_of_day_greeting():
    hour = datetime.now(NG_TZ).hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def honorific(gender: str, warm: bool = True) -> str:
    """Returns the address term to use. warm=True uses the softer 'mummy/daddy'
    style; warm=False uses the more formal 'ma/sir' style — both requested,
    so we mix them naturally across messages."""
    if gender == "female":
        return "mummy" if warm else "ma"
    else:
        return "daddy" if warm else "sir"

def greet(context, warm: bool = True) -> str:
    """Builds e.g. 'Good morning mummy' or 'Good evening sir' using stored
    gender + live time of day. Falls back gracefully if gender isn't set yet."""
    gender = context.user_data.get("gender", "male")
    return f"{time_of_day_greeting()} {honorific(gender, warm)}"

def name_or_blank(context) -> str:
    name = context.user_data.get("name", "")
    return name.split()[0] if name else ""

def personal_line(context, warm: bool = True) -> str:
    """A short personalized opener combining greeting + first name, e.g.
    'Good afternoon mummy Chioma,' — used at the top of major screens."""
    name = name_or_blank(context)
    base = greet(context, warm)
    return f"{base} {name}," if name else f"{base},"

# ============ DATA CAPTURE ============

def save_customer_record(user, context, event: str, detail: str = ""):
    """Appends a row to customers.csv every time something meaningful happens
    (onboarding complete, order placed, exchange requested, etc.)."""
    file_exists = os.path.exists(CUSTOMERS_FILE)
    try:
        with open(CUSTOMERS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "telegram_id", "telegram_username", "name", "phone", "gender", "event", "detail"])
            writer.writerow([
                datetime.now(NG_TZ).isoformat(timespec="seconds"),
                user.id,
                user.username or "",
                context.user_data.get("name", ""),
                context.user_data.get("phone", ""),
                context.user_data.get("gender", ""),
                event,
                detail,
            ])
    except Exception as e:
        logging.warning(f"Could not write customer record: {e}")

# ============ CATALOG ============
# Structure: SERVICES -> CATEGORIES -> ITEMS
# Prices are the real source-site prices with 10% already deducted.
# Each item has a short "hype" line shown together with its image when tapped.

PACKAGING_CATEGORIES = {
    "pkg_bags": {
        "label": "Paper Bags 🛍️",
        "gallery_intro": True,  # show style gallery before the item list
        "items": [
            {
                "id": "pb1",
                "name": "X-Large Paper Bag (A2 Landscape)",
                "price": 675,
                "moq": 100,
                "image": "https://inklets.com.ng/wp-content/uploads/2024/09/x-large-paper-bag.jpg",
                "note": "Full colour branding, rope handles — 10% off applied",
                "hype": "This is a beautiful choice 💅 — big, bold, and made to turn heads the moment a customer walks out with it swinging from their hand.",
            },
            {
                "id": "pb2",
                "name": "Christmas Themed Gift Bag (Twisted Handle)",
                "price": 10125,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/christmas-gift-bag.jpg",
                "note": "Seasonal print, twisted paper handle — 10% off applied",
                "hype": "Festive, warm, and unforgettable — this one makes every gift feel like an event.",
            },
            {
                "id": "pb3",
                "name": "Good Time Kraft (Brown) Gift Bag, Rope Handle",
                "price": 360,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/kraft-gift-bag.jpg",
                "note": "Natural kraft finish, rope handles — 10% off applied",
                "hype": "Simple, earthy, premium — the kind of bag that quietly says your brand has taste.",
            },
            {
                "id": "pb4",
                "name": "Healthy Food Kraft Bag",
                "price": 360,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/healthy-food-bag.jpg",
                "note": "Food-safe kraft, printed design — 10% off applied",
                "hype": "Sturdy and food-safe, this bag carries your meals and your brand name with equal pride.",
            },
        ],
    },
    "pkg_nylon": {
        "label": "Ziplock & Mailer Nylon Bags 🧴",
        "gallery_intro": True,
        "items": [
            {
                "id": "nl1",
                "name": "Frosted Ziplock Nylon Bag (Custom Branded)",
                "price": 90,
                "moq": 100,
                "image": "https://inklets.com.ng/wp-content/uploads/poly-bag.jpg",
                "note": "Matte frosted finish, resealable zip, your logo printed — 10% off applied",
                "hype": "Clock it 💅 — this soft matte finish is exactly the premium unboxing feel that keeps customers coming back for more.",
            },
            {
                "id": "nl2",
                "name": "Courier Mailer Bag (Matte, Custom Branded)",
                "price": 135,
                "moq": 100,
                "image": "https://inklets.com.ng/wp-content/uploads/poly-bag.jpg",
                "note": "Tamper-evident seal, tear-proof, full colour print — 10% off applied",
                "hype": "Bold, durable, and beautifully branded — the first thing your customer touches should feel this good.",
            },
        ],
    },
    "pkg_labels": {
        "label": "Labels & Stickers 🏷️",
        "items": [
            {
                "id": "lb1",
                "name": "Custom Product Labels (Roll of 500)",
                "price": 13500,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/label-roll.jpg",
                "note": "Waterproof vinyl, full colour — 10% off applied",
                "hype": "Small detail, big impact — this is how a product looks finished and trustworthy on a shelf.",
            },
            {
                "id": "lb2",
                "name": "Branded Sticker Sheets (A4, pack of 50)",
                "price": 9000,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/sticker-sheet.jpg",
                "note": "Glossy or matte finish — 10% off applied",
                "hype": "Versatile and vibrant — perfect for sealing, branding, and gifting all at once.",
            },
        ],
    },
    "pkg_boxes": {
        "label": "Boxes 🎁",
        "items": [
            {
                "id": "bx1",
                "name": "White Gable Box",
                "price": 315,
                "moq": 50,
                "image": "https://packhub.ng/wp-content/uploads/white-gable-box.jpg",
                "note": "Grease-resistant, customizable branding — 10% off applied",
                "hype": "Clean, elegant, and versatile — this box makes even a simple gift look intentional.",
            },
            {
                "id": "bx2",
                "name": "Corrugated Kraft (Brown) Large Box",
                "price": 450,
                "moq": 25,
                "image": "https://packhub.ng/wp-content/uploads/kraft-large-box.jpg",
                "note": "Recycled carton, sturdy for logistics — 10% off applied",
                "hype": "Tough enough for the road, beautiful enough for the unboxing — a real workhorse for your brand.",
            },
            {
                "id": "bx3",
                "name": "Bagasse Bento Cake Box",
                "price": 315,
                "moq": 50,
                "image": "https://packhub.ng/wp-content/uploads/bento-cake-box.jpg",
                "note": "Eco-friendly, leak resistant — 10% off applied",
                "hype": "Eco-conscious and elegant — your bakes deserve a box this thoughtful.",
            },
        ],
    },
    "pkg_books": {
        "label": "Books & Jotters 📚",
        "items": [
            {
                "id": "bk1",
                "name": "Branded A5 Jotter (100 pages)",
                "price": 675,
                "moq": 50,
                "image": "https://inklets.com.ng/wp-content/uploads/jotter.jpg",
                "note": "Custom cover print, spiral or perfect bound — 10% off applied",
                "hype": "A gift that gets used every single day — your brand, in their hands, again and again.",
            },
        ],
    },
    "pkg_plastic": {
        "label": "Plastic Packs 🧴",
        "items": [
            {
                "id": "pl1",
                "name": "Branded Poly Bags (pack of 100)",
                "price": 4500,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/poly-bag.jpg",
                "note": "Tamper-evident, custom print — 10% off applied",
                "hype": "Reliable, tidy, and unmistakably yours — the small touch that builds big trust.",
            },
        ],
    },
}

PRINTING_CATEGORIES = {
    "prt_banners": {
        "label": "Banners 🖼️",
        "items": [
            {
                "id": "bn1",
                "name": "Roll-Up Banner (85x200cm)",
                "price": 13500,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/rollup-banner.jpg",
                "note": "Includes stand, full colour print — 10% off applied",
                "hype": "This is the kind of presence that makes people stop mid-walk and ask about your brand.",
            },
        ],
    },
    "prt_stickers": {
        "label": "SAV Stickers 🏷️",
        "items": [
            {
                "id": "sv1",
                "name": "SAV Vinyl Sticker (per sqm)",
                "price": 4050,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/sav-sticker.jpg",
                "note": "Outdoor durable, custom cut — 10% off applied",
                "hype": "Weatherproof and sharp — built to keep your brand looking fresh outdoors for years.",
            },
        ],
    },
    "prt_shirts": {
        "label": "Shirts 👕",
        "items": [
            {
                "id": "sh1",
                "name": "Branded Round Neck T-Shirt",
                "price": 4500,
                "moq": 20,
                "image": "https://inklets.com.ng/wp-content/uploads/round-neck-tshirt.jpg",
                "note": "100% cotton, custom print/embroidery — 10% off applied",
                "hype": "Comfortable, clean, and walking billboard-worthy — your team will actually enjoy wearing this.",
            },
        ],
    },
    "prt_caps": {
        "label": "Caps 🧢",
        "items": [
            {
                "id": "cp1",
                "name": "Branded Face Cap",
                "price": 3150,
                "moq": 20,
                "image": "https://inklets.com.ng/wp-content/uploads/face-cap.jpg",
                "note": "Embroidered or printed logo — 10% off applied",
                "hype": "Sharp, simple, and always on-brand — the easiest merch win there is.",
            },
        ],
    },
    "prt_pens": {
        "label": "Biro Pens 🖊️",
        "items": [
            {
                "id": "bp1",
                "name": "Branded Biro Pen (box of 50)",
                "price": 9000,
                "moq": 1,
                "image": "https://inklets.com.ng/wp-content/uploads/biro-pen.jpg",
                "note": "Custom logo print — 10% off applied",
                "hype": "A tiny item that travels far — your logo, in a hundred hands, a hundred places.",
            },
        ],
    },
    "prt_mugs": {
        "label": "Mock Cups / Mugs 🍵",
        "items": [
            {
                "id": "mg1",
                "name": "Branded Ceramic Mug",
                "price": 2700,
                "moq": 20,
                "image": "https://inklets.com.ng/wp-content/uploads/branded-mug.jpg",
                "note": "Dishwasher-safe print — 10% off applied",
                "hype": "Morning coffee, afternoon tea — your brand becomes part of their daily ritual.",
            },
        ],
    },
    "prt_aprons": {
        "label": "Aprons 🥻",
        "items": [
            {
                "id": "ap1",
                "name": "Branded Kitchen Apron",
                "price": 3600,
                "moq": 10,
                "image": "https://inklets.com.ng/wp-content/uploads/apron.jpg",
                "note": "Durable fabric, logo print — 10% off applied",
                "hype": "Professional, practical, and proud — this is how a serious kitchen brand looks.",
            },
        ],
    },
}

# Real Edo State billboard listings (source: Alternative Adverts), 10% discount applied
BILLBOARDS = [
    {"id": "bb1", "name": "96 Sheet Landscape Billboard, Sapele Rd by Ikpopan Junction",
     "location": "Sapele Road by Ikpopan Junction, Edo State", "price": 585000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/11/96-Sheet-Landscape-Billboard-Benin-Sapele-Road-By-Ikpopan-Junction-Edo-State-300x300.jpg"},
    {"id": "bb2", "name": "Gantry Billboard, New Benin Market FTF Uselu Share",
     "location": "New Benin Market, FTF Uselu Share, Edo State", "price": 801000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Gantry-Billboard-New-Benin-Market-FTF-Uselu-Share-Edo-State-300x300.jpg"},
    {"id": "bb3", "name": "Gantry Billboard, New Lagos Road by New Benin Market",
     "location": "New Lagos Road by New Benin Market, Edo State", "price": 1440000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Gantry-Billboard-New-Lagos-Road-By-New-Benin-Market-Edo-State-300x300.jpg"},
    {"id": "bb4", "name": "Outdoor Unipole Billboard, University of Benin",
     "location": "University of Benin, Edo State", "price": 810000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Outdoor-Unipole-Billboard-By-University-Of-Benin-Edo-State-300x300.jpg"},
    {"id": "bb5", "name": "Portrait Billboard, Ikpoba Hill by Ramat Park",
     "location": "Ikpoba Hill by Ramat Park, Edo State", "price": 675000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Advertising-Billboard-Ikpoba-Hill-By-Ramat-Park-Edo-State-300x300.jpg"},
    {"id": "bb6", "name": "Portrait Billboard, Siluko Road",
     "location": "Siluko Road, Benin City, Edo State", "price": 360000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Advertising-Billboard-Siluko-Road-Benin-Edo-State-300x300.jpg"},
    {"id": "bb7", "name": "Portrait Billboard, Mission Road by Unity Bank",
     "location": "Mission Road by Unity Bank, Benin City, Edo State", "price": 540000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Along-Mission-Road-By-Unity-Bank-Benin-Edo-State-300x300.jpg"},
    {"id": "bb8", "name": "Portrait Billboard, Benin-Abuja Road",
     "location": "Benin-Abuja Road, Edo State", "price": 315000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Benin-along-Abuja-Road-Edo-State-300x300.jpg"},
    {"id": "bb9", "name": "Portrait Billboard, Benin-Lagos Road by UNIBEN",
     "location": "Benin-Lagos Road by University of Benin, Edo State", "price": 675000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-Benin-lagos-Road-By-Uni-Benin-Edo-State-300x300.jpg"},
    {"id": "bb10", "name": "Portrait Billboard, TV Road by 5 Junction Roundabout",
     "location": "TV Road by 5 Junction Roundabout, Edo State", "price": 315000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Portrait-Billboard-TV-Road-By-5-Junction-Round-About-Edo-State-300x300.jpg"},
    {"id": "bb11", "name": "Unipole Billboard, Ekewan Road by University",
     "location": "Ekewan Road by University, Edo State", "price": 675000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Unipole-Advertising-Billboard-Ekewan-Road-By-University-Edo-State-300x300.jpg"},
    {"id": "bb12", "name": "Unipole Billboard, Along Agbor/Onitsha Road",
     "location": "Agbor/Onitsha Road, Edo State", "price": 351000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Unipole-Billboard-Along-Agbor-Onitsha-Road-Edo-State-300x300.jpg"},
    {"id": "bb13", "name": "Unipole Billboard, Benin-Lagos Road Opposite Uselu Market",
     "location": "Benin-Lagos Road, Opposite Uselu Market, Edo State", "price": 405000,
     "image": "https://alternativeadverts.com/wp-content/uploads/2024/05/Unipole-Billboard-Benin-Lagos-Road-Opposite-Uselu-Market-Edo-State-300x300.jpg"},
]
BILLBOARD_PERIOD = "month"

# ─────────────────────────────────────────────────────────────
# ONLINE ADVERTISEMENT — rebuilt per spec
# ─────────────────────────────────────────────────────────────

PLATFORM_LOGOS = {
    "whatsapp": "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg.png",
    "instagram": "https://upload.wikimedia.org/wikipedia/commons/9/95/Instagram_logo_2022.svg.png",
    "snapchat": "https://upload.wikimedia.org/wikipedia/en/c/c4/Snapchat_logo.svg.png",
    "facebook": "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg.png",
    "tiktok": "https://upload.wikimedia.org/wikipedia/en/a/a9/TikTok_logo.svg.png",
}

# WhatsApp Nigerian marketplace group posting tiers (36 states coverage)
WHATSAPP_TIERS = [
    {"id": "wa1", "groups": 50, "price": 5000, "desc": "Great starter reach across active Nigerian buy & sell groups."},
    {"id": "wa2", "groups": 100, "price": 10000, "desc": "Wider reach — ideal for product launches and promos."},
    {"id": "wa3", "groups": 250, "price": 25000, "desc": "Serious visibility across many states at once."},
    {"id": "wa4", "groups": 500, "price": 50000, "desc": "Near nationwide coverage — built for big pushes."},
    {"id": "wa5", "groups": 1000, "price": 100000, "desc": "1000 super active marketplace buy & sell groups — our biggest push, covering all 36 states."},
]

# Real influencer roster from Mysogi (mysogi.com.ng), price = listed rate + 10%
# Influencers marked "estimated" had their exact per-post price cut off in the
# source screenshot; those are scaled sensibly against the confirmed rates below
# (visible range: ₦5,000 - ₦150,000 per post) and should be confirmed/adjusted
# by you before quoting a client directly.
INFLUENCERS = [
    {"id": "inf1", "name": "__e.l.o.n.a", "type": "Influencer", "followers": 77500, "price": 110000, "estimated": False},
    {"id": "inf2", "name": "Naomi", "type": "Influencer", "followers": 14700, "price": 77000, "estimated": False},
    {"id": "inf3", "name": "Ari Debby", "type": "Influencer", "followers": 86000, "price": 165000, "estimated": False},
    {"id": "inf4", "name": "Purplethelamb", "type": "Influencer", "followers": 29000, "price": 66000, "estimated": False},
    {"id": "inf5", "name": "Nkecci", "type": "Influencer", "followers": 37500, "price": 88000, "estimated": False},
    {"id": "inf6", "name": "The CU Student", "type": "Influencer", "followers": 184000, "price": 5500, "estimated": False},
    {"id": "inf7", "name": "Legalnaija", "type": "Blogger", "followers": 19300, "price": 22000, "estimated": False},
    {"id": "inf8", "name": "Campus Hubb", "type": "Blogger", "followers": 22000, "price": 11000, "estimated": False},
    {"id": "inf9", "name": "Kythegod", "type": "Influencer", "followers": 40000, "price": 33000, "estimated": False},
    {"id": "inf10", "name": "Futagrammm", "type": "Blogger", "followers": 108000, "price": 33000, "estimated": False},
    {"id": "inf11", "name": "Egbamitv", "type": "Influencer", "followers": 34000, "price": 33000, "estimated": False},
    {"id": "inf12", "name": "Mr Alabi", "type": "Influencer", "followers": 325000, "price": 66000, "estimated": False},
    {"id": "inf13", "name": "ElegantSlayers", "type": "Blogger", "followers": 366000, "price": 55000, "estimated": False},
    # Estimated (price not visible in source screenshot) — scaled by follower count
    {"id": "inf14", "name": "Dabi", "type": "Influencer", "followers": 50700, "price": 39000, "estimated": True},
    {"id": "inf15", "name": "dubemm._", "type": "Influencer", "followers": 111000, "price": 44000, "estimated": True},
    {"id": "inf16", "name": "prettyboyelvis_", "type": "Influencer", "followers": 13700, "price": 17000, "estimated": True},
    {"id": "inf17", "name": "Zabeth", "type": "Influencer", "followers": 107000, "price": 44000, "estimated": True},
    {"id": "inf18", "name": "Suzan Ade Coker", "type": "Influencer", "followers": 358000, "price": 132000, "estimated": True},
    {"id": "inf19", "name": "laerry", "type": "Influencer", "followers": 300000, "price": 121000, "estimated": True},
    {"id": "inf20", "name": "Samsmooth", "type": "Influencer", "followers": 135000, "price": 55000, "estimated": True},
    {"id": "inf21", "name": "Incredible Noble", "type": "Influencer", "followers": 448000, "price": 143000, "estimated": True},
    {"id": "inf22", "name": "Nanah", "type": "Influencer", "followers": 22700, "price": 22000, "estimated": True},
    {"id": "inf23", "name": "Cocainna", "type": "Influencer", "followers": 423000, "price": 138000, "estimated": True},
    {"id": "inf24", "name": "Meileekk", "type": "Influencer", "followers": 20200, "price": 22000, "estimated": True},
    {"id": "inf25", "name": "Nifemi EO", "type": "Influencer", "followers": 28700, "price": 27500, "estimated": True},
    {"id": "inf26", "name": "Modola", "type": "Actor", "followers": 141000, "price": 55000, "estimated": True},
    {"id": "inf27", "name": "FAVLEO", "type": "Influencer", "followers": 25000, "price": 27500, "estimated": True},
    {"id": "inf28", "name": "Stephaaney001", "type": "Influencer", "followers": 105000, "price": 44000, "estimated": True},
    {"id": "inf29", "name": "Hotgirltife", "type": "Influencer", "followers": 21700, "price": 22000, "estimated": True},
    {"id": "inf30", "name": "Glory.cu", "type": "Influencer", "followers": 15300, "price": 17000, "estimated": True},
    {"id": "inf31", "name": "Latchenko", "type": "Influencer", "followers": 112000, "price": 44000, "estimated": True},
]

EXCHANGE_ASSETS = ["USDT", "RMB", "SOL", "BTC", "ETH"]

# ============ CONVERSATION STATES ============
(
    AWAITING_GENDER,
    AWAITING_NAME,
    AWAITING_PHONE,
    AWAITING_ORDER_QTY,
    AWAITING_ORDER_CONTACT,
    AWAITING_ORDER_PROOF,
    AWAITING_BILLBOARD_CONTACT,
    AWAITING_BILLBOARD_PROOF,
    AWAITING_EXCHANGE_AMOUNT,
    AWAITING_EXCHANGE_CONTACT,
) = range(10)

# ============ HELPERS ============

def find_item(category_dict, item_id):
    for cat in category_dict.values():
        for item in cat["items"]:
            if item["id"] == item_id:
                return item
    return None

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Packaging", callback_data="svc_packaging")],
        [InlineKeyboardButton("🖨️ Printing", callback_data="svc_printing")],
        [InlineKeyboardButton("📢 Advertisement", callback_data="svc_advertisement")],
        [InlineKeyboardButton("💱 Exchange", callback_data="svc_exchange")],
    ])

def is_onboarded(context) -> bool:
    return bool(context.user_data.get("name") and context.user_data.get("phone") and context.user_data.get("gender"))

# ============ ONBOARDING (gender -> name -> phone) ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_onboarded(context):
        await send_main_menu(update, context, first_time=False)
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👩 Female", callback_data="gender_female")],
        [InlineKeyboardButton("👨 Male", callback_data="gender_male")],
    ])
    await update.message.reply_text(
        "✨ *Welcome to Affirmative Group Holdings* ✨\n\n"
        "Before we begin, may I know how to address you properly?",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    return AWAITING_GENDER

async def gender_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = "female" if query.data == "gender_female" else "male"
    context.user_data["gender"] = gender

    term = honorific(gender, warm=False)
    await query.edit_message_text(
        f"Lovely, thank you {term} 🙏\n\nAnd what should I call you? Please type your full name."
    )
    return AWAITING_NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    first = name_or_blank(context)
    await update.message.reply_text(
        f"Beautiful to meet you, {first} 🤝\n\n"
        f"Lastly, please share your phone number so our team can reach you about your orders."
    )
    return AWAITING_PHONE

async def phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    save_customer_record(update.effective_user, context, event="onboarded")

    greeting = personal_line(context, warm=True)
    await update.message.reply_text(
        f"{greeting} welcome truly — it's a pleasure having you here 💛\n\n"
        f"We help businesses across Nigeria stand out — from premium packaging "
        f"and print production, to outdoor & online advertising, and a trusted "
        f"currency exchange desk, all in one place.\n\n"
        f"Let's get you exactly what you came for. Choose a service below 👇"
    )
    await send_main_menu(update, context, first_time=True)
    return ConversationHandler.END

async def send_main_menu(update, context, first_time: bool):
    try:
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as img:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img,
                    caption="Your Packaging. Your Brand. Our Craft.",
                    reply_markup=main_menu_keyboard(),
                )
            return
    except Exception:
        pass

    text = f"{personal_line(context)} what would you like to explore today?" if not first_time else "What would you like to explore today?"
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, reply_markup=main_menu_keyboard()
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"🏠 {personal_line(context)} where next?"
    try:
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=main_menu_keyboard())

# ============ PACKAGING & PRINTING (shared logic) ============

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service = query.data.replace("svc_", "")
    categories = PACKAGING_CATEGORIES if service == "packaging" else PRINTING_CATEGORIES
    context.user_data["service"] = service

    keyboard = [[InlineKeyboardButton(cat["label"], callback_data=f"cat_{service}_{key}")] for key, cat in categories.items()]
    keyboard.append([InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")])

    title = "📦 *Packaging Services*" if service == "packaging" else "🖨️ *Printing Services*"
    text = f"{personal_line(context)}\n\n{title}\n\nChoose a category:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, service, cat_key = query.data.split("_", 2)
    categories = PACKAGING_CATEGORIES if service == "packaging" else PRINTING_CATEGORIES
    category = categories[cat_key]
    context.user_data["service"] = service
    context.user_data["cat_key"] = cat_key

    # Aesthetic style intro for bag-style categories, described in words rather
    # than shown as photos, since the reference looks (Elexio/Malika Modesty/
    # Luxe/Zevora/Lissen) carry other brands' logos — real order images below
    # are from your own catalog.
    if category.get("gallery_intro") and not context.user_data.get(f"seen_gallery_{cat_key}"):
        context.user_data[f"seen_gallery_{cat_key}"] = True
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=(
                f"{personal_line(context)} think soft matte finishes, bold logos, "
                f"resealable zips, tear-proof mailers — the kind of packaging people "
                f"screenshot and repost ✨\n\n"
                f"Now here's what we can craft for *you*:"
            ),
            parse_mode="Markdown",
        )

    keyboard = [
        [InlineKeyboardButton(f"{item['name'][:35]} — ₦{item['price']:,}", callback_data=f"item_{item['id']}")]
        for item in category["items"]
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"svc_{service}")])

    text = f"*{category['label']}*\n\nTap an item to view details & order:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_item_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item_id = query.data.replace("item_", "")
    service = context.user_data.get("service", "packaging")
    categories = PACKAGING_CATEGORIES if service == "packaging" else PRINTING_CATEGORIES
    item = find_item(categories, item_id)
    context.user_data["item"] = item

    hype = item.get("hype", "This is a wonderful pick — you're going to love it.")
    caption = (
        f"{hype}\n\n"
        f"*{item['name']}*\n"
        f"💵 ₦{item['price']:,} per unit\n"
        f"📦 MOQ: {item['moq']} units\n"
        f"📝 {item['note']}\n\n"
        f"Tap below to order."
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Order This", callback_data="order_item")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data=f"cat_{service}_{context.user_data.get('cat_key')}")],
    ]
    try:
        await context.bot.send_photo(
            chat_id=query.message.chat_id, photo=item["image"], caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown",
        )
        await query.message.delete()
    except Exception:
        try:
            await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception:
            await context.bot.send_message(chat_id=query.message.chat_id, text=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def order_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = context.user_data["item"]
    await query.message.reply_text(
        f"Excellent choice, {name_or_blank(context)} 🙌\n\n"
        f"How many units of *{item['name']}* would you like? (minimum {item['moq']})",
        parse_mode="Markdown",
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
        await update.message.reply_text(f"⚠️ Minimum order quantity is {item['moq']}. Please enter {item['moq']} or more.")
        return AWAITING_ORDER_QTY

    total = qty * item["price"]
    context.user_data["qty"] = qty
    context.user_data["total"] = total

    await update.message.reply_text(
        f"✅ *{item['name']}* x {qty}\n💵 Total: ₦{total:,}\n\n"
        f"Please type your *delivery address* so we can get this to you.",
        parse_mode="Markdown",
    )
    return AWAITING_ORDER_CONTACT

async def order_item_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer_info"] = update.message.text
    item = context.user_data["item"]
    total = context.user_data["total"]
    qty = context.user_data["qty"]

    save_customer_record(update.effective_user, context, event="order_placed",
                          detail=f"{item['name']} x{qty} = ₦{total:,}")

    await update.message.reply_text(
        f"Got it, {name_or_blank(context)} ✅\n\n{BANK_DETAILS}\n\n💵 *Amount to pay: ₦{total:,}*\n\n"
        f"📸 Once paid, send a screenshot of your transfer here.",
        parse_mode="Markdown",
    )

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *New Order*\n"
            f"Item: {item['name']}\nQty: {qty}\nTotal: ₦{total:,}\n"
            f"Name: {context.user_data.get('name')}\nPhone: {context.user_data.get('phone')}\n"
            f"Address: {context.user_data['customer_info']}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"Awaiting payment screenshot.",
            parse_mode="Markdown",
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
            ADMIN_CHAT_ID, photo.file_id,
            caption=(
                f"💰 *Payment Screenshot Received*\nItem: {item.get('name')}\nQty: {qty}\nTotal: ₦{total:,}\n"
                f"Name: {context.user_data.get('name')}\nPhone: {context.user_data.get('phone')}\n"
                f"Address: {customer_info}\n"
                f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
                f"✅ Reply here to confirm manually with the customer."
            ),
            parse_mode="Markdown",
        )

    await update.message.reply_text(
        f"✅ Screenshot received, {name_or_blank(context)}! Your order is *pending confirmation*.\n"
        f"You'll hear from us shortly.\n\nThank you for choosing Affirmative Group Holdings 🙌",
        parse_mode="Markdown",
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
    text = f"{personal_line(context)}\n\n📢 *Advertisement Services*\n\nChoose a channel:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_billboards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"{b['name'][:35]} — ₦{b['price']:,}", callback_data=f"bb_{b['id']}")] for b in BILLBOARDS]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="svc_advertisement")])
    text = f"🛣️ *Available Billboard Slots in Edo State*\nPrices are per {BILLBOARD_PERIOD}. Tap one to see photo, location & book:"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_billboard_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board_id = query.data.replace("bb_", "")
    board = next(b for b in BILLBOARDS if b["id"] == board_id)
    context.user_data["board"] = board

    caption = (
        f"This spot is 🔥 — high visibility and always in front of the right eyes.\n\n"
        f"📍 *{board['name']}*\n🗺️ {board['location']}\n💵 ₦{board['price']:,} / {BILLBOARD_PERIOD}\n\n"
        f"Tap below to book."
    )
    keyboard = [
        [InlineKeyboardButton(f"✅ Book — ₦{board['price']:,}", callback_data="confirm_billboard")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data="ad_outdoor")],
    ]
    try:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=board["image"], caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        await query.message.delete()
    except Exception:
        await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def confirm_billboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    board = context.user_data["board"]
    context.user_data["total"] = board["price"]
    await query.message.reply_text(
        f"✅ *{board['name']}* — 1 {BILLBOARD_PERIOD}\n💵 Total: ₦{board['price']:,}\n\n"
        f"Please type your *full name and preferred start date*.",
        parse_mode="Markdown",
    )
    return AWAITING_BILLBOARD_CONTACT

async def billboard_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer_info"] = update.message.text
    board = context.user_data["board"]
    total = context.user_data["total"]
    save_customer_record(update.effective_user, context, event="billboard_booked", detail=f"{board['name']} = ₦{total:,}")

    await update.message.reply_text(f"Got it ✅\n\n{BANK_DETAILS}\n\n💵 *Amount to pay: ₦{total:,}*\n\n📸 Once paid, send a screenshot of your transfer here.", parse_mode="Markdown")

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *New Billboard Booking*\nBoard: {board['name']}\nLocation: {board['location']}\nTotal: ₦{total:,}\n"
            f"Name: {context.user_data.get('name')}\nPhone: {context.user_data.get('phone')}\n"
            f"Details: {context.user_data['customer_info']}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\nAwaiting payment screenshot.",
            parse_mode="Markdown",
        )
    return AWAITING_BILLBOARD_PROOF

async def billboard_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = context.user_data.get("board", {})
    total = context.user_data.get("total", 0)
    customer_info = context.user_data.get("customer_info", "Unknown")
    photo = update.message.photo[-1]

    if ADMIN_CHAT_ID:
        await context.bot.send_photo(
            ADMIN_CHAT_ID, photo.file_id,
            caption=(
                f"💰 *Payment Screenshot Received*\nBoard: {board.get('name')}\nTotal: ₦{total:,}\n"
                f"Name: {context.user_data.get('name')}\nPhone: {context.user_data.get('phone')}\nDetails: {customer_info}\n"
                f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n✅ Reply here to confirm manually."
            ),
            parse_mode="Markdown",
        )
    await update.message.reply_text(
        f"✅ Screenshot received, {name_or_blank(context)}! Your booking is *pending confirmation*.\n"
        f"You'll hear from us within a few hours.\n\nThank you for choosing Affirmative Group Holdings 🙌",
        parse_mode="Markdown",
    )
    return ConversationHandler.END

# ---- Online Advertisement submenu ----

async def show_online_ad_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌟 Influencer Ads/Post", callback_data="onl_influencer")],
        [InlineKeyboardButton("💬 WhatsApp Marketing", callback_data="onl_whatsapp")],
        [InlineKeyboardButton("📸 Instagram UGC Ads", callback_data="onl_instagram")],
        [InlineKeyboardButton("👻 Snapchat Ads", callback_data="onl_snapchat")],
        [InlineKeyboardButton("📘 Facebook Ads", callback_data="onl_facebook")],
        [InlineKeyboardButton("🎵 TikTok Ads", callback_data="onl_tiktok")],
        [InlineKeyboardButton("⬅️ Back", callback_data="svc_advertisement")],
    ]
    text = f"{personal_line(context)}\n\n💻 *Online Advertisement*\n\nWhich channel would you like to explore?"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_platform_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """For Instagram/Snapchat/Facebook/TikTok — shows the platform logo + brief info + contact CTA."""
    query = update.callback_query
    await query.answer()
    platform = query.data.replace("onl_", "")

    names = {"instagram": "Instagram UGC Ads", "snapchat": "Snapchat Ads", "facebook": "Facebook Ads", "tiktok": "TikTok Ads"}
    descriptions = {
        "instagram": "Authentic, native-feeling content created by real users to promote your brand on Instagram — Reels, Stories, and feed posts that convert because they don't feel like ads.",
        "snapchat": "Reach a young, highly engaged Nigerian audience with vertical video ads built for Snapchat's format.",
        "facebook": "Targeted Facebook ad campaigns built around your exact audience — age, location, interests, and buying intent.",
        "tiktok": "High-energy, trend-native TikTok ad content designed to stop the scroll and drive real engagement.",
    }
    name = names.get(platform, platform.title())
    desc = descriptions.get(platform, "")
    logo = PLATFORM_LOGOS.get(platform)

    caption = (
        f"{personal_line(context)} here's what we offer on *{name}* 👇\n\n"
        f"{desc}\n\n"
        f"Message our team directly to scope out your campaign and get a custom quote."
    )
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="ad_online")]]
    try:
        if logo:
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=logo, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            await query.message.delete()
        else:
            await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_whatsapp_tiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{t['groups']} groups — ₦{t['price']:,}", callback_data=f"watier_{t['id']}")]
        for t in WHATSAPP_TIERS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="ad_online")])

    caption = (
        f"{personal_line(context)} 💬 *WhatsApp Marketing*\n\n"
        f"We post your product/service directly into active Nigerian WhatsApp "
        f"buy & sell marketplace groups spanning all 36 states — real people, "
        f"real buyers, real reach.\n\nChoose a package:"
    )
    logo = PLATFORM_LOGOS.get("whatsapp")
    try:
        if logo:
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=logo, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            await query.message.delete()
        else:
            await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def whatsapp_tier_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tier_id = query.data.replace("watier_", "")
    tier = next(t for t in WHATSAPP_TIERS if t["id"] == tier_id)
    context.user_data["wa_tier"] = tier

    text = (
        f"*{tier['groups']} Groups Package* — ₦{tier['price']:,}\n\n"
        f"{tier['desc']}\n\n"
        f"Ready to move forward, {name_or_blank(context)}?"
    )
    keyboard = [
        [InlineKeyboardButton(f"✅ Proceed — ₦{tier['price']:,}", callback_data="confirm_watier")],
        [InlineKeyboardButton("⬅️ Back", callback_data="onl_whatsapp")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def confirm_whatsapp_tier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tier = context.user_data["wa_tier"]
    save_customer_record(update.effective_user, context, event="whatsapp_marketing_request",
                          detail=f"{tier['groups']} groups = ₦{tier['price']:,}")

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *WhatsApp Marketing Request*\nPackage: {tier['groups']} groups — ₦{tier['price']:,}\n"
            f"Name: {context.user_data.get('name')}\nPhone: {context.user_data.get('phone')}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}",
            parse_mode="Markdown",
        )
    await query.edit_message_text(
        f"✅ Request received, {name_or_blank(context)}! Our team will reach out on "
        f"{context.user_data.get('phone', 'your number')} shortly to confirm payment and get your post live.\n\n"
        f"Thank you for choosing Affirmative Group Holdings 🙌"
    )

# ---- Influencer roster ----

async def show_influencer_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{inf['name']} ({inf['followers']:,}) — ₦{inf['price']:,}", callback_data=f"inf_{inf['id']}")]
        for inf in INFLUENCERS
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="ad_online")])
    text = (
        f"{personal_line(context)}\n\n🌟 *Influencer Ads / Posts*\n\n"
        f"Real influencers, real audiences. Tap a name to see their profile and book a post:"
    )
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_influencer_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inf_id = query.data.replace("inf_", "")
    inf = next(i for i in INFLUENCERS if i["id"] == inf_id)
    context.user_data["influencer"] = inf

    note = " (estimated rate — to be reconfirmed)" if inf.get("estimated") else ""
    caption = (
        f"This is a fantastic pick, {name_or_blank(context)} — great engagement and a loyal audience 🔥\n\n"
        f"*{inf['name']}*\n{inf['type']} · 👥 {inf['followers']:,} followers\n"
        f"💵 ₦{inf['price']:,} per post{note}\n\n"
        f"Ready to book this influencer?"
    )
    keyboard = [
        [InlineKeyboardButton(f"✅ Book — ₦{inf['price']:,}", callback_data="confirm_influencer")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data="onl_influencer")],
    ]
    await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def confirm_influencer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inf = context.user_data["influencer"]
    save_customer_record(update.effective_user, context, event="influencer_booking_request",
                          detail=f"{inf['name']} = ₦{inf['price']:,}")

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 *Influencer Booking Request*\nInfluencer: {inf['name']} ({inf['followers']:,} followers)\nRate: ₦{inf['price']:,}\n"
            f"Name: {context.user_data.get('name')}\nPhone: {context.user_data.get('phone')}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}",
            parse_mode="Markdown",
        )
    await query.edit_message_text(
        f"✅ Request received, {name_or_blank(context)}! Our team will reach out shortly to finalize "
        f"content details and payment.\n\nThank you for choosing Affirmative Group Holdings 🙌"
    )

# ============ EXCHANGE ============

async def show_exchange_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("💵 Buy", callback_data="ex_buy"), InlineKeyboardButton("💴 Sell", callback_data="ex_sell")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")],
    ]
    text = f"{personal_line(context)}\n\n💱 *Currency & Crypto Exchange*\n\nWhat would you like to do?"
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_exchange_assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.replace("ex_", "")
    context.user_data["ex_action"] = action
    keyboard = [[InlineKeyboardButton(asset, callback_data=f"exasset_{asset}")] for asset in EXCHANGE_ASSETS]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="svc_exchange")])
    verb = "buy" if action == "buy" else "sell"
    await query.edit_message_text(f"What do you want to {verb}?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def exchange_ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    asset = query.data.replace("exasset_", "")
    context.user_data["ex_asset"] = asset
    action = context.user_data.get("ex_action", "buy")
    await query.edit_message_text(f"How much {asset} would you like to {action}? (enter the amount, e.g. '500' or '0.05')", parse_mode="Markdown")
    return AWAITING_EXCHANGE_AMOUNT

async def exchange_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ex_amount"] = update.message.text
    await update.message.reply_text(
        f"Please confirm the phone number our team should reach you on for this transaction.",
        parse_mode="Markdown",
    )
    return AWAITING_EXCHANGE_CONTACT

async def exchange_contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_info = update.message.text
    action = context.user_data.get("ex_action", "buy")
    asset = context.user_data.get("ex_asset", "?")
    amount = context.user_data.get("ex_amount", "?")
    save_customer_record(update.effective_user, context, event="exchange_request", detail=f"{action} {amount} {asset}")

    await update.message.reply_text(
        f"✅ Request received, {name_or_blank(context)}! Our team will contact you shortly with the current "
        f"rate to complete your transaction.\n\nThank you for choosing Affirmative Group Holdings 🙌",
        parse_mode="Markdown",
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"💱 *New Exchange Request*\nAction: {action.upper()}\nAsset: {asset}\nAmount: {amount}\n"
            f"Name: {context.user_data.get('name')}\nPhone: {contact_info}\n"
            f"Telegram: @{update.effective_user.username or update.effective_user.first_name}\n\n"
            f"⚠️ Reply directly to the customer with your rate to proceed.",
            parse_mode="Markdown",
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

    onboarding_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AWAITING_GENDER: [CallbackQueryHandler(gender_chosen, pattern="^gender_(male|female)$")],
            AWAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
            AWAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

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

    app.add_handler(onboarding_conv)
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(order_conv)
    app.add_handler(billboard_conv)
    app.add_handler(exchange_conv)

    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^svc_(packaging|printing)$"))
    app.add_handler(CallbackQueryHandler(show_ad_options, pattern="^svc_advertisement$"))
    app.add_handler(CallbackQueryHandler(show_exchange_options, pattern="^svc_exchange$"))
    app.add_handler(CallbackQueryHandler(show_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_item_detail, pattern="^item_"))

    app.add_handler(CallbackQueryHandler(show_billboards, pattern="^ad_outdoor$"))
    app.add_handler(CallbackQueryHandler(show_online_ad_menu, pattern="^ad_online$"))
    app.add_handler(CallbackQueryHandler(show_billboard_detail, pattern="^bb_"))

    app.add_handler(CallbackQueryHandler(show_influencer_list, pattern="^onl_influencer$"))
    app.add_handler(CallbackQueryHandler(show_influencer_detail, pattern="^inf_"))
    app.add_handler(CallbackQueryHandler(confirm_influencer, pattern="^confirm_influencer$"))

    app.add_handler(CallbackQueryHandler(show_whatsapp_tiers, pattern="^onl_whatsapp$"))
    app.add_handler(CallbackQueryHandler(whatsapp_tier_detail, pattern="^watier_"))
    app.add_handler(CallbackQueryHandler(confirm_whatsapp_tier, pattern="^confirm_watier$"))

    app.add_handler(CallbackQueryHandler(show_platform_intro, pattern="^onl_(instagram|snapchat|facebook|tiktok)$"))

    app.add_handler(CallbackQueryHandler(show_exchange_assets, pattern="^ex_(buy|sell)$"))

    print("Affirmative Group Holdings bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

# ============================================
# NOTES
# - customers.csv is created/appended in this same folder on every meaningful
#   event (onboarding, order, booking, exchange request) — open it in Excel
#   or Google Sheets whenever you want to review or pitch with the data.
# - Influencer prices marked "estimated": True in INFLUENCERS were scaled from
#   follower count since their exact per-post rate was cut off in your
#   screenshots. Please reconfirm those before quoting a client directly.
# - The nylon/mailer bag "aesthetic gallery" text references the premium look
#   you shared (Elexio/Malika Modesty/Luxe/Zevora/Lissen-style matte bags) as
#   inspiration copy — actual order images shown are still Inklets/PackHub
#   product photos, since the reference photos carry other brands' logos.
# ============================================
