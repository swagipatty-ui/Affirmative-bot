# YUYU Ads — WhatsApp Automation Blueprint (Make.com)

WhatsApp doesn't let you run custom bot code the way Telegram does — you need
either Meta's official WhatsApp Business Platform API, or a middle-layer tool
like Make.com, Twilio, or 360dialog that connects to it. Since you want
free/near-free and phone-first, **Make.com's WhatsApp Business connector** is
the right starting point.

## What you need to set up (one-time, ~30–45 mins)

1. **WhatsApp Business App** (free) — already have this per your setup.
2. **Meta Business Suite account** — free, links to your WhatsApp number.
3. **Make.com free account** — 1,000 operations/month free tier, enough to start.
4. In Make.com: search "WhatsApp Business Cloud" connector, follow the
   authentication steps (it walks you through linking your Meta Business
   account and phone number).

## The automation flow (build this as a Make.com Scenario)

```
[Trigger: New WhatsApp Message Received]
        │
        ▼
[Router: check message content]
        │
        ├── Contains "book" / "billboard" / "price"
        │         │
        │         ▼
        │   [Send: Billboard list + prices as template message]
        │         │
        │         ▼
        │   [Wait for reply: which billboard?]
        │         │
        │         ▼
        │   [Send: Bank details + amount for selected slot]
        │         │
        │         ▼
        │   [Wait for reply: image/screenshot]
        │         │
        │         ▼
        │   [Forward screenshot + customer number to YOUR WhatsApp/Telegram]
        │         │
        │         ▼
        │   [Send customer: "Received! Confirming within a few hours."]
        │
        └── Anything else
                  │
                  ▼
            [Send: "Hi! Type BOOK to see billboard slots, or PRICE for pricing."]
```

## Declutter-sales flow (same skeleton, second scenario)

```
[Trigger: New WhatsApp Message Received]
        │
        ▼
[Router: check message content]
        │
        ├── Contains "sale" / "declutter" / product keyword
        │         │
        │         ▼
        │   [Send: Current declutter catalog — photos + prices]
        │         │
        │         ▼
        │   [Wait for reply: item name]
        │         │
        │         ▼
        │   [Send: Bank details for that item's price]
        │         │
        │         ▼
        │   [Wait for screenshot → forward to you → confirm to customer]
```

## Monetization layer on top of both bots

1. **Booking commission** — your core margin per billboard/LED slot booked.
2. **Featured listing fee** — vendors pay ₦X/week to have their slot shown
   first in the bot's list (edit the BILLBOARDS order/config to reflect paid
   placement).
3. **Instant-confirm premium** — customers who want same-hour confirmation
   (vs standard next-business-day) pay a small rush fee; route this as a
   separate button/reply option in both bots.

## Why this order (bot digital storefront, WhatsApp trust layer, app later)

- **Telegram bot**: fully automated, built and ready now, costs nothing to run.
- **WhatsApp flow**: takes more setup (Meta account, Make.com scenario) but
  reaches the much larger WhatsApp-first Nigerian audience — build this
  second, once the Telegram version proves the flow works.
- **App**: hold off until you have repeat customers who'd value a saved
  wallet/loyalty system — premature right now.

## Next steps for you

1. Get your Telegram bot token from @BotFather, drop it into `bot.py`, run it.
2. Test the full flow yourself (View Billboards → pick one → pick duration →
   send fake screenshot) to make sure it feels right before sharing the link.
3. Once Telegram is live and tested, set up the Make.com WhatsApp connector
   using the flow diagram above — I can help you build the exact Make.com
   scenario step-by-step when you're ready for that stage.
