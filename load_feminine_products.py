"""
Script to replace all existing shop products with Feminine Sanitary Care products.
Run with: /var/www/venv/myshop/bin/python3 /var/www/venv/myshop/load_feminine_products.py
"""
import os
import sys
import django
import urllib.request
import shutil
from pathlib import Path
from decimal import Decimal
from datetime import date

# ── Setup Django ──────────────────────────────────────────────────────────────
sys.path.insert(0, '/var/www/venv/myshop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from shop.models import Category, Product

# ── New product catalogue ─────────────────────────────────────────────────────
CATEGORIES = [
    {
        "name": "Sanitary Pads",
        "slug": "sanitary-pads",
        "products": [
            {
                "name": "Always Maxi Thick Long 8's Pads",
                "slug": "always-maxi-thick-long-8s-pads",
                "description": (
                    "Trusted protection you can count on. Always Maxi Thick Long pads offer "
                    "heavy-flow coverage with a thick absorbent core that locks away leaks. "
                    "The soft cottony top layer stays gentle on your skin, while the contoured "
                    "shape moves with your body for all-day comfort. Pack of 8 pads — ideal for "
                    "regular to heavy flow days."
                ),
                "price": Decimal("549.00"),
            },
            {
                "name": "Always Maxi Thick E/Long Duo 14 Pads",
                "slug": "always-maxi-thick-elong-duo-14-pads",
                "description": (
                    "Double the protection with the Always Maxi Thick Extra Long Duo pack. "
                    "Designed for extra coverage during heavy flow, these pads are longer at "
                    "the back to prevent leaks even overnight. The duo pack (14 pads) gives you "
                    "excellent value, combining superior absorbency with a comfortable, wings-free "
                    "fit that stays securely in place."
                ),
                "price": Decimal("637.00"),
            },
            {
                "name": "Always Ultra Thin Long Pads 32s",
                "slug": "always-ultra-thin-long-pads-32s",
                "description": (
                    "Barely-there comfort meets powerful protection. Always Ultra Thin Long pads "
                    "feature an ultra-thin core that absorbs quickly, keeping you dry and confident. "
                    "Flexible wings hold the pad in place so you can move freely. This value pack "
                    "of 32 pads is perfect for month-long protection without compromise."
                ),
                "price": Decimal("1110.00"),
            },
            {
                "name": "Always Ultra Day & Night Sanitary Pads Size 3 with Wings 20s",
                "slug": "always-ultra-day-night-pads-size-3-wings-20s",
                "description": (
                    "One pad for round-the-clock protection — day and night. Size 3 with flexible "
                    "wings, these Always Ultra pads combine super absorbency with a smooth, "
                    "breathable top sheet that wicks moisture away in seconds. The extra-long "
                    "design prevents nighttime leaks, so you wake up fresh and worry-free. Pack of 20."
                ),
                "price": Decimal("2999.00"),
            },
            {
                "name": "Always Herbal Ultra Clean Pads 7pcs",
                "slug": "always-herbal-ultra-clean-pads-7pcs",
                "description": (
                    "Experience the freshness of nature with Always Herbal Ultra Clean pads. "
                    "Infused with natural herbal extracts, these pads offer a gentle, soothing "
                    "sensation while providing superior absorption. The breathable cover keeps "
                    "you feeling clean and fresh throughout the day. Pack of 7 — great for lighter "
                    "flow days or as a panty liner alternative."
                ),
                "price": Decimal("899.00"),
            },
            {
                "name": "Always Soft Maxi Thick Long Sanitary Pads 14s",
                "slug": "always-soft-maxi-thick-long-14s",
                "description": (
                    "Comfort redefined. Always Soft Maxi Thick Long pads feature a uniquely soft "
                    "cover that feels gentle against sensitive skin. The thick absorbent core "
                    "provides heavy-flow protection while the longer length gives you peace of "
                    "mind all day long. Comes with a soft, quilted top layer for maximum skin "
                    "friendliness. Pack of 14 pads."
                ),
                "price": Decimal("1150.00"),
            },
            {
                "name": "Always Sanitary Pads Soft Maxi Thick 16x16 XL Duo",
                "slug": "always-sanitary-pads-soft-maxi-thick-16x16-xl-duo",
                "description": (
                    "Maximum coverage for maximum confidence. The Always Maxi Thick XL Duo pack "
                    "gives you 32 pads in total (2 x 16) — each pad designed with an extra-wide "
                    "surface for full protection. Ideal for heavy flow days, these XL pads have "
                    "a soft cottony cover and a deep absorbent core to keep leaks completely at bay."
                ),
                "price": Decimal("637.00"),
            },
            {
                "name": "Always Ultra Thin Overnight Pads Size 4 with Wings 80ct",
                "slug": "always-ultra-thin-overnight-pads-size-4-wings-80ct",
                "description": (
                    "Sleep soundly every night of the month. Always Ultra Thin Size 4 Overnight "
                    "pads are longer, wider, and more absorbent — engineered specifically for "
                    "nighttime use. Wings prevent side leaks, while the ultra-thin core keeps "
                    "you feeling dry and comfortable. Unscented formula is perfect for sensitive "
                    "skin. Bulk pack of 80 for long-lasting supply."
                ),
                "price": Decimal("9990.00"),
            },
        ],
    },
    {
        "name": "Panty Liners",
        "slug": "panty-liners",
        "products": [
            {
                "name": "Always Dailies Fresh & Protect Panty Liners 20s",
                "slug": "always-dailies-fresh-protect-panty-liners-20s",
                "description": (
                    "Freshness every single day. Always Dailies Fresh & Protect panty liners are "
                    "ultra-thin and flexible, designed for daily light discharge and spotting. "
                    "Their breathable material allows your skin to breathe while the OdourLock "
                    "technology neutralises unwanted odours for up to 8 hours of freshness. "
                    "Pack of 20 individually wrapped liners."
                ),
                "price": Decimal("350.00"),
            },
            {
                "name": "Always Discreet Panty Liners Sensitive 30s",
                "slug": "always-discreet-panty-liners-sensitive-30s",
                "description": (
                    "Specially formulated for sensitive skin. Always Discreet Sensitive panty liners "
                    "use a hypoallergenic, fragrance-free, soft flexi-cover that moulds to your "
                    "body's natural curves. Ideal for everyday light-flow protection, spotting, "
                    "or light bladder leaks. Super slim profile fits discreetly in all underwear "
                    "styles. Pack of 30."
                ),
                "price": Decimal("420.00"),
            },
        ],
    },
    {
        "name": "Tampons",
        "slug": "tampons",
        "products": [
            {
                "name": "Tampax Pearl Tampons Regular Absorbency 18s",
                "slug": "tampax-pearl-tampons-regular-18s",
                "description": (
                    "Feel protected and forget you're wearing it. Tampax Pearl tampons feature a "
                    "LeakGuard Braid that helps stop leaks before they happen, and a smooth plastic "
                    "applicator for comfortable insertion. The pearl-shaped tip guides easily and "
                    "expands to fit your body's shape. Regular absorbency, suitable for light to "
                    "medium flow days. Pack of 18."
                ),
                "price": Decimal("950.00"),
            },
            {
                "name": "Tampax Compak Super Plus Tampons 16s",
                "slug": "tampax-compak-super-plus-tampons-16s",
                "description": (
                    "Super-plus protection in a compact carry. Tampax Compak Super Plus offers "
                    "maximum absorbency for the heaviest flow days. The compact applicator is "
                    "pocket-sized yet unfolds to full size for easy use. Fitted with a security "
                    "veil that wraps around the tampon, preventing side leaks. Pack of 16 — "
                    "discreet enough for your handbag."
                ),
                "price": Decimal("1100.00"),
            },
        ],
    },
    {
        "name": "Feminine Wipes & Tissues",
        "slug": "feminine-wipes-tissues",
        "products": [
            {
                "name": "Velvex Facial Tissue Silver 140 Sheets",
                "slug": "velvex-facial-tissue-silver-140-sheets",
                "description": (
                    "Softness you can feel instantly. Velvex Silver facial tissues are 2-ply and "
                    "dermatologically tested, making them gentle enough for sensitive skin. "
                    "Perfect for intimate cleansing, makeup removal, or everyday facial care. "
                    "The silver embossed design adds a touch of elegance to your vanity. "
                    "140 double-strength sheets per box."
                ),
                "price": Decimal("149.00"),
            },
            {
                "name": "Velvex Facial Tissue Petal Soft 140 Sheets",
                "slug": "velvex-facial-tissue-petal-soft-140-sheets",
                "description": (
                    "Petal-soft comfort for the most delicate skin. Velvex Petal Soft tissues are "
                    "crafted with a silky lotion-free formula that stays gentle even on irritated "
                    "skin. Ideal as a feminine hygiene tissue for quick, clean freshening up on the "
                    "go. The floral-embossed finish is as beautiful as it is functional. 140 sheets."
                ),
                "price": Decimal("149.00"),
            },
            {
                "name": "Velvex Facial Tissue Embossed Blue 80 Sheets",
                "slug": "velvex-facial-tissue-embossed-blue-80-sheets",
                "description": (
                    "A trusted everyday essential. Velvex Embossed Blue facial tissues offer "
                    "reliable 2-ply softness in a compact box perfect for your desk, bathroom, "
                    "or handbag. Lint-free and hypoallergenic, they're safe for use around "
                    "sensitive areas. Rated 4.9/5 by customers for their exceptional softness "
                    "and durability. 80 sheets per box."
                ),
                "price": Decimal("140.00"),
            },
            {
                "name": "Intimate Feminine Cleansing Wipes 20s",
                "slug": "intimate-feminine-cleansing-wipes-20s",
                "description": (
                    "Gentle, pH-balanced freshness wherever you need it. These intimate feminine "
                    "wipes are alcohol-free and dermatologically tested to maintain your body's "
                    "natural pH balance. Infused with aloe vera and chamomile extracts, each wipe "
                    "delivers a cooling, soothing sensation. Perfect for freshening up after the "
                    "gym, travel, or during your period. Pack of 20 individually folded wipes."
                ),
                "price": Decimal("280.00"),
            },
        ],
    },
    {
        "name": "Menstrual Cups & Discs",
        "slug": "menstrual-cups-discs",
        "products": [
            {
                "name": "Organicup Menstrual Cup Size A (Pre-childbirth)",
                "slug": "organicup-menstrual-cup-size-a",
                "description": (
                    "Make a sustainable switch. The OrganiCup Menstrual Cup is made from 100% "
                    "medical-grade silicone — free of BPA, latex, and bleach. It holds up to "
                    "3× more than a regular pad or tampon and lasts up to 10 years, saving you "
                    "money and reducing waste. Size A is designed for those who have not given "
                    "birth vaginally. Easy to insert, wear for up to 12 hours, remove, rinse and "
                    "reuse. Comes with a breathable organic cotton pouch."
                ),
                "price": Decimal("2500.00"),
            },
            {
                "name": "Lunette Menstrual Cup Model 1 (Light Flow)",
                "slug": "lunette-menstrual-cup-model-1",
                "description": (
                    "Award-winning Finnish design for effortless period care. The Lunette Model 1 "
                    "is a soft, flexible menstrual cup perfect for light to medium flow days and "
                    "beginners. Made from FDA-registered, food-grade silicone with no harmful "
                    "chemicals. Holds 25ml of fluid, can be worn safely for up to 12 hours. "
                    "Reusable for years, making it the most eco-friendly period product available. "
                    "Includes a cotton storage bag and full user guide."
                ),
                "price": Decimal("2800.00"),
            },
        ],
    },
    {
        "name": "Feminine Hygiene Wash",
        "slug": "feminine-hygiene-wash",
        "products": [
            {
                "name": "Lactacyd Feminine Wash Daily 250ml",
                "slug": "lactacyd-feminine-wash-daily-250ml",
                "description": (
                    "Clinically proven to maintain your natural pH balance. Lactacyd Daily Feminine "
                    "Wash contains natural milk extracts (Lactic Acid) that mirror your body's "
                    "own protective layer. It gently cleanses, soothes dryness, and prevents "
                    "irritation — without disturbing the delicate intimate flora. Gynaecologist "
                    "tested and recommended. Suitable for daily use. 250ml pump bottle."
                ),
                "price": Decimal("750.00"),
            },
            {
                "name": "Femfresh Intimate Wash Extra Soothing 250ml",
                "slug": "femfresh-intimate-wash-extra-soothing-250ml",
                "description": (
                    "Extra soothing care for sensitive days. Femfresh Extra Soothing Intimate Wash "
                    "is enriched with aloe vera and witch hazel to calm and protect your most "
                    "sensitive skin. Its soap-free, pH-balanced formula is ideal during and after "
                    "your period when skin is most delicate. Dermatologist and gynaecologist tested. "
                    "Free from harsh chemicals. 250ml bottle."
                ),
                "price": Decimal("820.00"),
            },
        ],
    },
]

# ── Helper: download and save product image ───────────────────────────────────
today = date.today()
MEDIA_DIR = Path('/var/www/venv/myshop/media/products') / str(today.year) / f'{today.month:02d}' / f'{today.day:02d}'
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

PLACEHOLDER_IMAGES = {
    "sanitary-pads":          "https://i.imgur.com/placeholder.png",  # will use generated images
    "panty-liners":           "",
    "tampons":                "",
    "feminine-wipes-tissues": "",
    "menstrual-cups-discs":   "",
    "feminine-hygiene-wash":  "",
}

# ── Main data-load logic ──────────────────────────────────────────────────────
def run():
    print("🗑  Deleting existing products and categories...")
    Product.objects.all().delete()
    Category.objects.all().delete()
    print("   Done.\n")

    for cat_data in CATEGORIES:
        cat, _ = Category.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={"name": cat_data["name"]},
        )
        print(f"📂 Category: {cat.name}")

        for prod_data in cat_data["products"]:
            prod, created = Product.objects.get_or_create(
                slug=prod_data["slug"],
                defaults={
                    "category": cat,
                    "name": prod_data["name"],
                    "description": prod_data["description"],
                    "price": prod_data["price"],
                    "available": True,
                },
            )
            if not created:
                # update fields if already exists (re-run safety)
                prod.name = prod_data["name"]
                prod.description = prod_data["description"]
                prod.price = prod_data["price"]
                prod.category = cat
                prod.available = True
                prod.save()

            status = "✅ created" if created else "🔄 updated"
            print(f"   {status}: {prod.name} — KSh {prod.price}")

    total_cats = Category.objects.count()
    total_prods = Product.objects.count()
    print(f"\n✔  Done! {total_cats} categories and {total_prods} products loaded.")


if __name__ == "__main__":
    run()
