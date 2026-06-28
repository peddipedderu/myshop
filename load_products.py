#!/usr/bin/env python
"""
Load comprehensive ecommerce product catalog for PinkCycle Shop.
Inspired by Jumia Kenya and Kilimall with Kenya-focused pricing in KES.
Run with: python manage.py shell < load_products.py
OR: python load_products.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from shop.models import Category, Product, Brand, Tag
from django.utils.text import slugify
from decimal import Decimal
from django.utils import timezone

# ─── BRANDS ────────────────────────────────────────────────────────────────────
brands_data = [
    ('Samsung', 'samsung', 'https://www.samsung.com'), ('Apple', 'apple', 'https://www.apple.com'),
    ('Tecno', 'tecno', ''), ('Infinix', 'infinix', 'https://www.infinixmobility.com'),
    ('Xiaomi', 'xiaomi', 'https://www.mi.com'), ('Nokia', 'nokia', 'https://www.nokia.com'),
    ('Oppo', 'oppo', 'https://www.oppo.com'), ('HP', 'hp', 'https://www.hp.com'),
    ('Dell', 'dell', 'https://www.dell.com'), ('Lenovo', 'lenovo', 'https://www.lenovo.com'),
    ('LG', 'lg', 'https://www.lg.com'), ('Sony', 'sony', 'https://www.sony.com'),
    ('Hisense', 'hisense', 'https://www.hisense.com'), ('Bruhm', 'bruhm', ''),
    ('Von', 'von', ''), ('Ramtons', 'ramtons', 'https://www.ramtons.com'),
    ('Nunix', 'nunix', ''), ('Ariel', 'ariel', ''), ('Dettol', 'dettol', ''),
    ('Unilever', 'unilever', 'https://www.unilever.com'), ('Nike', 'nike', 'https://www.nike.com'),
    ('Adidas', 'adidas', 'https://www.adidas.com'), ('Puma', 'puma', 'https://www.puma.com'),
    ('Generic', 'generic', ''), ('PinkCycle', 'pinkcycle', 'https://pinkcycle.co.ke'),
    ('Vitafoam', 'vitafoam', ''), ('Melanie', 'melanie', ''),
    ('Nasco', 'nasco', ''), ('Syinix', 'syinix', ''),
]

brands = {}
for name, slug_str, website in brands_data:
    brand, _ = Brand.objects.get_or_create(slug=slug_str, defaults={'name': name, 'website': website})
    brands[slug_str] = brand
print(f"✓ {len(brands)} brands created/loaded")

# ─── TAGS ─────────────────────────────────────────────────────────────────────
tags_data = [
    'new-arrival', 'bestseller', 'featured', 'deal', 'trending',
    'electronics', 'fashion', 'home', 'beauty', 'health',
    'gaming', 'sport', 'outdoor', 'kitchen', 'baby',
    'office', 'school', 'discount', 'limited-edition', 'eco-friendly'
]
tags = {}
for tag_name in tags_data:
    tag, _ = Tag.objects.get_or_create(slug=tag_name, defaults={'name': tag_name.replace('-', ' ').title()})
    tags[tag_name] = tag
print(f"✓ {len(tags)} tags created/loaded")

# ─── CATEGORIES ───────────────────────────────────────────────────────────────
categories_data = [
    # (name, slug, parent_slug, is_featured, sort_order, description)
    ('Electronics', 'electronics', None, True, 1, 'Phones, laptops, TVs and more'),
    ('Phones & Tablets', 'phones-tablets', 'electronics', True, 1, 'Smartphones, feature phones and tablets'),
    ('Laptops & Computers', 'laptops-computers', 'electronics', True, 2, 'Laptops, desktops and accessories'),
    ('TVs & Audio', 'tvs-audio', 'electronics', True, 3, 'Televisions, speakers and headphones'),
    ('Camera & Photography', 'camera-photography', 'electronics', False, 4, 'Cameras, drones and accessories'),
    ('Gaming', 'gaming', 'electronics', True, 5, 'Gaming consoles, games and accessories'),

    ('Fashion', 'fashion', None, True, 2, "Men's and Women's fashion"),
    ("Women's Fashion", 'womens-fashion', 'fashion', True, 1, "Dresses, tops, jeans and more"),
    ("Men's Fashion", 'mens-fashion', 'fashion', True, 2, "Shirts, trousers, suits and more"),
    ('Shoes & Sneakers', 'shoes-sneakers', 'fashion', True, 3, 'All types of footwear'),
    ('Bags & Luggage', 'bags-luggage', 'fashion', False, 4, 'Handbags, backpacks and luggage'),
    ('Watches & Jewelry', 'watches-jewelry', 'fashion', False, 5, 'Timepieces and accessories'),

    ('Home & Kitchen', 'home-kitchen', None, True, 3, 'Home appliances, furniture and kitchen'),
    ('Kitchen Appliances', 'kitchen-appliances', 'home-kitchen', True, 1, 'Cookers, blenders, microwaves'),
    ('Home Appliances', 'home-appliances', 'home-kitchen', True, 2, 'Fridges, washing machines, ACs'),
    ('Furniture & Decor', 'furniture-decor', 'home-kitchen', False, 3, 'Sofas, beds, tables and decor'),
    ('Bedding & Bath', 'bedding-bath', 'home-kitchen', False, 4, 'Bedsheets, towels and pillows'),

    ('Beauty & Health', 'beauty-health', None, True, 4, 'Skincare, hair care and wellness'),
    ('Skincare', 'skincare', 'beauty-health', True, 1, 'Moisturizers, serums and face care'),
    ('Hair Care', 'hair-care', 'beauty-health', True, 2, 'Shampoos, conditioners and styling'),
    ('Makeup', 'makeup', 'beauty-health', True, 3, 'Foundation, lipstick and more'),
    ('Health & Wellness', 'health-wellness', 'beauty-health', False, 4, 'Vitamins, fitness and health'),
    ('Fragrances', 'fragrances', 'beauty-health', False, 5, 'Perfumes and body sprays'),

    ('Sports & Outdoors', 'sports-outdoors', None, True, 5, 'Sports gear, fitness and outdoor'),
    ('Exercise & Fitness', 'exercise-fitness', 'sports-outdoors', True, 1, 'Gym equipment and fitness gear'),
    ('Sports Clothing', 'sports-clothing', 'sports-outdoors', True, 2, 'Activewear and sports uniforms'),
    ('Outdoor & Camping', 'outdoor-camping', 'sports-outdoors', False, 3, 'Tents, hiking gear and camping'),

    ('Baby & Toys', 'baby-toys', None, True, 6, 'Baby essentials and toys'),
    ('Baby Clothing', 'baby-clothing', 'baby-toys', True, 1, 'Onesies, rompers and baby clothes'),
    ('Toys & Games', 'toys-games', 'baby-toys', True, 2, 'Educational toys and games'),

    ('Food & Beverages', 'food-beverages', None, True, 7, 'Groceries, snacks and drinks'),
    ('Groceries', 'groceries', 'food-beverages', True, 1, 'Daily essentials and pantry items'),

    ('Office & School', 'office-school', None, True, 8, 'Office supplies and school stationery'),
    ('Stationery', 'stationery', 'office-school', True, 1, 'Pens, notebooks and office supplies'),
    ('Printers & Ink', 'printers-ink', 'office-school', False, 2, 'Printers, toners and cartridges'),

    ('Automotive', 'automotive', None, False, 9, 'Car accessories and spare parts'),

    ('Community Shop', 'community-shop', None, True, 10, 'PinkCycle curated products'),
    ('Menstrual Products', 'menstrual-products', 'community-shop', True, 1, 'Eco-friendly period products'),
    ('Wellness Kits', 'wellness-kits', 'community-shop', True, 2, 'Health and wellness packages'),
    ('Books & Education', 'books-education', 'community-shop', True, 3, 'Empowerment books and resources'),
]

categories = {}
# First pass: top-level
for name, slug_str, parent_slug, is_featured, sort_order, desc in categories_data:
    if parent_slug is None:
        cat, _ = Category.objects.get_or_create(slug=slug_str, defaults={
            'name': name, 'is_featured': is_featured, 'sort_order': sort_order,
            'description': desc, 'parent': None
        })
        categories[slug_str] = cat

# Second pass: subcategories
for name, slug_str, parent_slug, is_featured, sort_order, desc in categories_data:
    if parent_slug is not None:
        parent = categories.get(parent_slug)
        cat, _ = Category.objects.get_or_create(slug=slug_str, defaults={
            'name': name, 'is_featured': is_featured, 'sort_order': sort_order,
            'description': desc, 'parent': parent
        })
        categories[slug_str] = cat

print(f"✓ {len(categories)} categories created/loaded")

# ─── PRODUCTS ─────────────────────────────────────────────────────────────────
def make_product(name, cat_slug, brand_slug, price, original_price=None,
                 description='', short_desc='', stock=50, is_featured=False,
                 is_bestseller=False, is_new_arrival=True, tag_slugs=None, sku=None):
    slug = slugify(name)
    if Product.objects.filter(slug=slug).exists():
        slug = slug + '-1'
    p, created = Product.objects.get_or_create(
        name=name,
        defaults={
            'slug': slug,
            'category': categories.get(cat_slug, categories.get('electronics')),
            'brand': brands.get(brand_slug, brands.get('generic')),
            'price': Decimal(str(price)),
            'original_price': Decimal(str(original_price)) if original_price else None,
            'description': description or f"{name} - Premium quality product available at PinkCycle Shop.",
            'short_description': short_desc or f"Quality {name} at the best price in Kenya.",
            'stock': stock,
            'available': True,
            'is_featured': is_featured,
            'is_bestseller': is_bestseller,
            'is_new_arrival': is_new_arrival,
            'sku': sku or slugify(name)[:20],
        }
    )
    if tag_slugs:
        for ts in tag_slugs:
            if ts in tags:
                p.tags.add(tags[ts])
    return p, created


products_data = [
    # ── PHONES ──────────────────────────────────────────────────────────────
    ("Samsung Galaxy A55 5G", "phones-tablets", "samsung", 49999, 54999,
     "Samsung Galaxy A55 5G with 6.6-inch Super AMOLED display, 50MP triple camera, 5000mAh battery and 5G connectivity. Features OIS for smoother videos and IP67 water resistance.",
     "5G smartphone with 50MP camera & 5000mAh battery", 30, True, True, True,
     ['bestseller', 'featured', 'electronics', 'trending'], "SAM-A55-5G"),

    ("Tecno Camon 30 Pro", "phones-tablets", "tecno", 29999, 34999,
     "Tecno Camon 30 Pro with 6.78-inch curved AMOLED display, 50MP front camera, 64MP rear camera and 5000mAh battery. Perfect for selfie lovers.",
     "Pro camera phone with 64MP AI camera", 40, True, False, True,
     ['new-arrival', 'trending', 'electronics'], "TEC-C30-PRO"),

    ("Infinix Note 40 Pro 5G", "phones-tablets", "infinix", 34999, 39999,
     "Infinix Note 40 Pro 5G with 6.78-inch AMOLED display, 108MP camera, 5000mAh battery and 68W fast charging. Dual 5G SIM support.",
     "5G phone with 108MP camera & 68W charging", 35, True, False, True,
     ['new-arrival', 'featured', 'electronics'], "INF-N40-5G"),

    ("Samsung Galaxy A15 4G", "phones-tablets", "samsung", 18999, 21999,
     "Samsung Galaxy A15 with 6.5-inch Super AMOLED display, 50MP triple camera, 5000mAh battery. Great entry-level smartphone.",
     "Affordable Samsung with 50MP camera", 60, False, True, False,
     ['bestseller', 'electronics'], "SAM-A15-4G"),

    ("Xiaomi Redmi 13C 4G", "phones-tablets", "xiaomi", 13999, 16999,
     "Xiaomi Redmi 13C with 6.74-inch IPS LCD display, 50MP AI camera, 5000mAh battery and MediaTek Helio G85 processor.",
     "Budget phone with 50MP camera & big battery", 80, False, True, False,
     ['bestseller', 'electronics'], "XIA-R13C"),

    ("Apple iPhone 15 128GB", "phones-tablets", "apple", 119999, 129999,
     "Apple iPhone 15 with 6.1-inch Super Retina XDR display, 48MP main camera with 2x optical zoom, A16 Bionic chip and USB-C charging.",
     "iPhone 15 with A16 Bionic & 48MP camera", 15, True, True, False,
     ['featured', 'trending', 'electronics'], "APL-IP15-128"),

    ("Tecno Spark 20 Pro", "phones-tablets", "tecno", 16999, 19499,
     "Tecno Spark 20 Pro with 6.78-inch display, 108MP rear camera, 5000mAh battery. Great value for money.",
     "108MP camera phone at budget price", 55, False, False, True,
     ['new-arrival', 'electronics'], "TEC-S20-PRO"),

    ("Samsung Galaxy Tab A8", "phones-tablets", "samsung", 32999, 36999,
     "Samsung Galaxy Tab A8 10.5-inch tablet with 128GB storage, 7040mAh battery, TFT display and quad speakers. Perfect for work and entertainment.",
     "10.5-inch tablet with 128GB & quad speakers", 25, False, True, False,
     ['bestseller', 'electronics'], "SAM-TABA8"),

    # ── LAPTOPS ─────────────────────────────────────────────────────────────
    ("HP 15s Core i5 11th Gen", "laptops-computers", "hp", 69999, 79999,
     "HP 15s with Intel Core i5-1135G7, 8GB RAM, 512GB SSD, 15.6-inch Full HD display and Windows 11 Home. Thin and light design perfect for students and professionals.",
     "Core i5 laptop with 512GB SSD & Windows 11", 20, True, True, False,
     ['bestseller', 'featured', 'electronics', 'office'], "HP-15S-I5"),

    ("Lenovo IdeaPad Slim 3", "laptops-computers", "lenovo", 54999, 64999,
     "Lenovo IdeaPad Slim 3 with AMD Ryzen 5, 8GB RAM, 512GB SSD, 15.6-inch display. Reliable everyday laptop with good battery life.",
     "AMD Ryzen 5 laptop with long battery life", 25, False, True, False,
     ['bestseller', 'electronics'], "LEN-IPS3"),

    ("Dell Inspiron 15 Core i3", "laptops-computers", "dell", 45999, 52999,
     "Dell Inspiron 15 with Intel Core i3-1215U, 8GB RAM, 256GB SSD, 15.6-inch FHD display. Dependable performance for everyday tasks.",
     "Affordable Dell laptop for students", 30, False, False, True,
     ['new-arrival', 'electronics', 'school'], "DEL-INS15-I3"),

    ("Lenovo ThinkBook 14 G4", "laptops-computers", "lenovo", 89999, 104999,
     "Lenovo ThinkBook 14 G4 with AMD Ryzen 5 5625U, 16GB RAM, 512GB SSD, 14-inch IPS display. Professional-grade laptop for productivity.",
     "Business laptop with AMD Ryzen 5 & 16GB RAM", 15, True, False, True,
     ['featured', 'electronics', 'office'], "LEN-TB14-G4"),

    # ── TVs ─────────────────────────────────────────────────────────────────
    ("Samsung 43-inch 4K Smart TV", "tvs-audio", "samsung", 54999, 62999,
     "Samsung 43-inch Crystal UHD 4K Smart TV with HDR, AirSlim design, Universal Remote Control and built-in Bixby assistant.",
     "4K Smart TV with HDR & built-in WiFi", 20, True, True, False,
     ['bestseller', 'featured', 'electronics'], "SAM-TV43-4K"),

    ("Hisense 55-inch QLED 4K TV", "tvs-audio", "hisense", 67999, 79999,
     "Hisense 55-inch QLED 4K Smart TV with Quantum Dot technology, Dolby Vision, HDMI 2.1 and VIDAA U6 Smart OS. Stunning picture quality.",
     "55-inch QLED 4K with Dolby Vision", 15, True, False, True,
     ['new-arrival', 'featured', 'electronics'], "HIS-55-QLED"),

    ("Sony 40-inch Full HD Smart TV", "tvs-audio", "sony", 42999, 49999,
     "Sony 40-inch Full HD Bravia TV with Android TV, Google Assistant, Chromecast built-in and X-Reality PRO processing engine.",
     "Sony Bravia with Android TV & Google Assistant", 20, False, True, False,
     ['bestseller', 'electronics'], "SON-TV40-FHD"),

    ("Syinix 32-inch HD Smart TV", "tvs-audio", "syinix", 21999, 25999,
     "Syinix 32-inch HD Smart TV with built-in WiFi, Android OS, 3 HDMI ports and 2 USB ports. Budget-friendly smart TV.",
     "32-inch budget smart TV with Android OS", 40, False, False, True,
     ['new-arrival', 'electronics'], "SYI-TV32"),

    # ── HOME APPLIANCES ──────────────────────────────────────────────────────
    ("Samsung 200L Double Door Fridge", "home-appliances", "samsung", 49999, 59999,
     "Samsung 200-litre No-Frost double door refrigerator with digital inverter, All-Around Cooling and cool select zone. Energy efficient.",
     "200L No-Frost fridge with digital inverter", 10, True, True, False,
     ['bestseller', 'featured', 'home'], "SAM-FRIDGE-200"),

    ("LG 7kg Front Load Washing Machine", "home-appliances", "lg", 59999, 72999,
     "LG 7kg Front Load Washing Machine with AI Direct Drive motor, TurboWash 360 technology, built-in WiFi and 14 wash programs.",
     "7kg front loader with AI motor & WiFi", 12, True, False, True,
     ['new-arrival', 'featured', 'home'], "LG-WM7-FL"),

    ("Von 3-Burner Gas Cooker", "kitchen-appliances", "von", 14999, 17999,
     "Von 3-burner gas cooker with 60cm stainless steel body, auto ignition, cast iron pan supports and safety valve. Durable and reliable.",
     "3-burner gas cooker with auto ignition", 30, False, True, False,
     ['bestseller', 'home', 'kitchen'], "VON-GC3-SS"),

    ("Ramtons Blender 1.5L", "kitchen-appliances", "ramtons", 3999, 5499,
     "Ramtons 1.5-litre blender with stainless steel blades, 600W motor, 3-speed settings and pulse function. Perfect for smoothies and juices.",
     "1.5L blender with 600W motor", 60, False, True, False,
     ['bestseller', 'home', 'kitchen'], "RAM-BL15"),

    ("Nunix 20L Microwave Oven", "kitchen-appliances", "nunix", 8999, 11999,
     "Nunix 20-litre solo microwave with 700W power, 5 power levels, 35-minute timer and defrost function. Compact and efficient.",
     "20L microwave with 5 power levels", 40, False, False, True,
     ['new-arrival', 'kitchen'], "NUN-MW20"),

    # ── BEAUTY & HEALTH ──────────────────────────────────────────────────────
    ("Cerave Moisturizing Cream 250ml", "skincare", "generic", 2499, 2999,
     "CeraVe Moisturizing Cream with 3 essential ceramides and hyaluronic acid. Fragrance-free, non-comedogenic and suitable for all skin types.",
     "Moisturizing cream with ceramides - for all skin types", 100, True, True, False,
     ['bestseller', 'beauty', 'health', 'featured'], "CER-MC250"),

    ("The Ordinary Niacinamide 10%", "skincare", "generic", 1999, 2499,
     "The Ordinary Niacinamide 10% + Zinc 1% serum to reduce blemishes, balance sebum and minimize pores. Vegan and cruelty-free.",
     "Niacinamide 10% serum for clear, even skin", 120, True, True, False,
     ['bestseller', 'featured', 'beauty'], "ORD-NIA10"),

    ("Dove Body Lotion 400ml", "skincare", "generic", 899, 1199,
     "Dove Nourishing Body Lotion with natural moisturising serum. Provides 48-hour moisturisation for silky, smooth skin.",
     "48-hour moisturising body lotion", 200, False, True, False,
     ['bestseller', 'beauty', 'health'], "DOV-BL400"),

    ("Garnier Vitamin C Serum 30ml", "skincare", "generic", 1499, 1999,
     "Garnier Vitamin C Super Glow Serum with 3.5% pure Vitamin C and Niacinamide. Brightens skin and reduces dark spots in 1 week.",
     "Vitamin C brightening serum - visible results in 1 week", 80, True, False, True,
     ['new-arrival', 'beauty', 'trending'], "GAR-VCS30"),

    ("Pantene Pro-V Shampoo 400ml", "hair-care", "generic", 699, 899,
     "Pantene Pro-V Repair & Protect Shampoo with Pro-Vitamin B5. Reduces hair damage up to 99% with regular use. For damaged hair.",
     "Repair shampoo with Pro-Vitamin B5", 150, False, True, False,
     ['bestseller', 'beauty'], "PAN-SHAM400"),

    ("MAC Studio Fix Foundation", "makeup", "generic", 4999, 5999,
     "MAC Studio Fix Fluid Foundation SPF 15 with 24-hour wear. Full coverage, matte finish available in 60+ shades. Dermatologist tested.",
     "Full coverage foundation SPF 15 - 60+ shades", 50, True, True, False,
     ['bestseller', 'featured', 'beauty', 'makeup'], "MAC-SFF"),

    ("Maybelline Fit Me Foundation", "makeup", "generic", 1999, 2499,
     "Maybelline Fit Me Matte + Poreless Foundation with natural finish. Blurs pores and controls shine for flawless natural-looking coverage.",
     "Pore-blurring matte foundation", 80, False, True, False,
     ['bestseller', 'beauty'], "MAY-FMF"),

    ("Nivea Men Body Spray 200ml", "fragrances", "generic", 549, 699,
     "Nivea Men Fresh Active deodorant body spray with 48-hour protection. Fresh masculine scent with 0% alcohol.",
     "48-hour protection body spray for men", 200, False, False, True,
     ['new-arrival', 'health'], "NIV-MBOYS200"),

    # ── FASHION ────────────────────────────────────────────────────────────
    ("Women's Floral Maxi Dress", "womens-fashion", "generic", 2999, 3999,
     "Elegant floral maxi dress with flowing silhouette. Made from breathable chiffon fabric. Available in multiple colors. Perfect for events and casual outings.",
     "Flowing chiffon maxi dress - multiple colors", 80, True, True, True,
     ['new-arrival', 'featured', 'fashion', 'trending'], "WF-FLMAX"),

    ("Men's Slim Fit Chino Trousers", "mens-fashion", "generic", 1999, 2499,
     "Slim fit chino trousers with stretch fabric for comfort. Available in khaki, navy, black and olive. Machine washable.",
     "Stretch chinos in 4 colors - slim fit", 100, False, True, False,
     ['bestseller', 'fashion'], "MF-CHINO"),

    ("Women's Sneakers - White", "shoes-sneakers", "nike", 7999, 9999,
     "Nike Women's Court Vision Low sneakers in classic white. Leather upper with padded collar and foam midsole for all-day comfort.",
     "Classic white leather sneakers", 60, True, True, True,
     ['new-arrival', 'featured', 'fashion', 'sport'], "NIKE-WCV-WHT"),

    ("Men's Running Shoes", "shoes-sneakers", "adidas", 8999, 11999,
     "Adidas Runfalcon 3.0 men's running shoes with Cloudfoam midsole for cushioning. Breathable mesh upper and non-slip rubber outsole.",
     "Lightweight running shoes with Cloudfoam cushioning", 50, False, True, True,
     ['new-arrival', 'sport', 'fashion'], "ADI-RF3-MEN"),

    ("Women's Leather Handbag", "bags-luggage", "generic", 3999, 5499,
     "Premium PU leather handbag with multiple compartments, detachable shoulder strap and gold-tone hardware. Available in black, brown and tan.",
     "Premium leather handbag with multiple pockets", 40, True, False, True,
     ['new-arrival', 'featured', 'fashion'], "WB-LEATH"),

    ("Men's Formal Shirt", "mens-fashion", "generic", 1499, 1999,
     "Classic formal shirt with slim fit cut, spread collar and mother-of-pearl buttons. Available in white, light blue and pale pink. 100% cotton.",
     "Slim fit 100% cotton formal shirt", 120, False, True, False,
     ['bestseller', 'fashion', 'office'], "MF-SHIRT"),

    ("Sneaker Air Max Style", "shoes-sneakers", "nike", 12999, 16999,
     "Nike Air Max inspired style with visible Air unit cushioning. Mesh upper for breathability with rubber traction outsole. Unisex design.",
     "Air cushion sneakers - unisex", 45, True, True, True,
     ['new-arrival', 'trending', 'featured', 'fashion'], "NIKE-AM"),

    # ── SPORTS ─────────────────────────────────────────────────────────────
    ("Yoga Mat Non-Slip 6mm", "exercise-fitness", "generic", 2499, 3499,
     "Premium non-slip yoga mat 6mm thick with alignment lines. Made from eco-friendly TPE material. Includes carry strap. Suitable for all yoga styles.",
     "6mm eco-friendly yoga mat with carry strap", 60, True, True, True,
     ['featured', 'sport', 'health', 'new-arrival'], "SP-YMAT6"),

    ("Adjustable Dumbbell Set 20kg", "exercise-fitness", "generic", 8999, 12999,
     "Adjustable dumbbell set 20kg with quick-change weight plates. Chrome-plated handles with knurled grip. Suitable for home gym workouts.",
     "Adjustable dumbbell set - up to 20kg per pair", 25, False, True, False,
     ['bestseller', 'sport', 'health'], "SP-DUMB20"),

    ("Football Nike Premier", "sports-clothing", "nike", 3499, 4499,
     "Nike Premier football with high-contrast graphic for visibility. Machine stitched for durability. Size 5. Suitable for recreational play.",
     "Nike Premier size 5 football", 80, False, True, False,
     ['bestseller', 'sport'], "NIKE-FOOT5"),

    # ── BABY & TOYS ─────────────────────────────────────────────────────────
    ("Baby Romper Set 3-Pack", "baby-clothing", "generic", 1999, 2499,
     "Adorable 3-piece baby romper set made from 100% organic cotton. Super soft and gentle on baby's skin. Available in 0-3, 3-6, 6-12 months.",
     "3-pack organic cotton baby rompers", 100, True, False, True,
     ['new-arrival', 'baby', 'featured'], "BB-ROMP3"),

    ("LEGO Classic Bricks 500pcs", "toys-games", "generic", 4999, 5999,
     "LEGO Classic creative brick box with 500 pieces in multiple colors. Stimulates creativity and motor skills. Suitable for ages 4+.",
     "500-piece creative LEGO set for ages 4+", 40, True, True, False,
     ['bestseller', 'featured', 'baby'], "LEG-C500"),

    # ── COMMUNITY SHOP / PINK CYCLE ─────────────────────────────────────────
    ("Reusable Menstrual Pads Set (5pcs)", "menstrual-products", "pinkcycle", 1499, 1999,
     "PinkCycle eco-friendly reusable menstrual pads - pack of 5 in various sizes. Made from organic cotton with waterproof backing. Washable and durable for up to 3 years.",
     "Eco-friendly reusable pads - save money & the planet", 200, True, True, True,
     ['featured', 'health', 'eco-friendly', 'bestseller'], "PC-RMPADS5"),

    ("Menstrual Cup - Medium", "menstrual-products", "pinkcycle", 1999, 2499,
     "PinkCycle medical-grade silicone menstrual cup. Holds 3x more than a tampon. Lasts up to 10 years. Comes with a cotton storage pouch.",
     "Medical grade silicone menstrual cup - 10 year lifespan", 150, True, True, True,
     ['featured', 'health', 'eco-friendly', 'bestseller'], "PC-MCUP-M"),

    ("Period Underwear 3-Pack", "menstrual-products", "pinkcycle", 3999, 4999,
     "PinkCycle leak-proof period underwear in 3 styles. Absorbs up to 4 tampons worth of flow. Machine washable. Available in S, M, L, XL, XXL.",
     "Leak-proof period underwear - 3 pack", 80, True, True, True,
     ['featured', 'health', 'eco-friendly', 'trending'], "PC-PUNK3"),

    ("Girls Empowerment Book Set", "books-education", "pinkcycle", 2999, 3999,
     "PinkCycle curated set of 3 empowerment books for teenage girls covering self-confidence, health education and life skills. Written by Kenyan authors.",
     "3 empowerment books for teenage girls", 100, True, False, True,
     ['new-arrival', 'featured', 'health', 'eco-friendly'], "PC-BOOKS3"),

    ("Women's Wellness Kit", "wellness-kits", "pinkcycle", 4999, 6999,
     "PinkCycle Women's Wellness Kit containing: herbal teas, aromatherapy oils, a self-care journal, and a relaxation guide. Perfect self-care gift.",
     "Complete wellness kit for women", 50, True, True, True,
     ['featured', 'health', 'bestseller', 'trending'], "PC-WKIT"),

    # ── OFFICE & SCHOOL ──────────────────────────────────────────────────────
    ("A4 Paper Ream 500 Sheets", "stationery", "generic", 699, 899,
     "High-quality A4 copy paper 80gsm, 500 sheets per ream. Suitable for all types of printers and copiers. Bright white finish.",
     "A4 80gsm paper - 500 sheets", 200, False, True, False,
     ['bestseller', 'office', 'school'], "OFF-A4REM"),

    ("Office Chair Ergonomic", "stationery", "generic", 16999, 22999,
     "Ergonomic office chair with adjustable lumbar support, breathable mesh back, armrests and height adjustment. Maximum weight 120kg.",
     "Ergonomic mesh office chair with lumbar support", 20, True, False, True,
     ['new-arrival', 'featured', 'office'], "OFF-CHAIR"),

    # ── GAMING ──────────────────────────────────────────────────────────────
    ("PS5 DualSense Controller", "gaming", "sony", 9999, 12999,
     "PlayStation 5 DualSense wireless controller with haptic feedback, adaptive triggers, built-in microphone and USB-C charging. White.",
     "PS5 DualSense with haptic feedback & adaptive triggers", 30, True, True, True,
     ['new-arrival', 'featured', 'gaming', 'trending', 'electronics'], "SON-DS5-WHT"),

    ("Xbox Game Pass Ultimate 3 Months", "gaming", "generic", 4999, 5999,
     "Xbox Game Pass Ultimate 3-month subscription with access to 100+ games, Xbox Live Gold, EA Play and cloud gaming.",
     "100+ games + Xbox Live Gold for 3 months", 999, True, True, True,
     ['featured', 'gaming', 'trending'], "XBOX-GP3M"),

    ("Gaming Headset RGB", "gaming", "generic", 4999, 6999,
     "Gaming headset with 7.1 surround sound, RGB lighting, noise-cancelling microphone and compatible with PC, PS4/5 and Xbox.",
     "7.1 surround gaming headset with RGB", 45, False, True, True,
     ['new-arrival', 'gaming', 'electronics'], "GAM-HS71"),
]

created_count = 0
updated_count = 0
for data in products_data:
    p, created = make_product(*data)
    if created:
        created_count += 1
    else:
        updated_count += 1

print(f"✓ Products: {created_count} created, {updated_count} already existed")
print("\n✅ Product catalog loaded successfully!")
print(f"   Total products: {Product.objects.count()}")
print(f"   Total categories: {Category.objects.count()}")
print(f"   Total brands: {Brand.objects.count()}")
