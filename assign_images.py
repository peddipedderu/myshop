"""
Assign product images in the database.
Run with: /var/www/venv/myshop/bin/python3 /var/www/venv/myshop/assign_images.py
"""
import os, sys, django
sys.path.insert(0, '/var/www/venv/myshop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from shop.models import Product

today = "2026/06/26"
base = f"products/{today}"

# Map slug-prefix -> image filename
IMAGE_MAP = {
    "always-maxi-thick-long-8s":            f"{base}/sanitary_pads.jpg",
    "always-maxi-thick-elong-duo":           f"{base}/sanitary_pads.jpg",
    "always-ultra-thin-long-pads-32s":       f"{base}/sanitary_pads.jpg",
    "always-ultra-day-night":                f"{base}/sanitary_pads.jpg",
    "always-herbal-ultra-clean":             f"{base}/sanitary_pads.jpg",
    "always-soft-maxi-thick-long-14s":       f"{base}/sanitary_pads.jpg",
    "always-sanitary-pads-soft-maxi":        f"{base}/sanitary_pads.jpg",
    "always-ultra-thin-overnight":           f"{base}/sanitary_pads.jpg",
    "always-dailies-fresh":                  f"{base}/panty_liners.jpg",
    "always-discreet-panty-liners":          f"{base}/panty_liners.jpg",
    "tampax-pearl":                          f"{base}/tampons.jpg",
    "tampax-compak":                         f"{base}/tampons.jpg",
    "velvex-facial-tissue-silver-140":       f"{base}/facial_tissues.jpg",
    "velvex-facial-tissue-petal-soft-140":   f"{base}/facial_tissues.jpg",
    "velvex-facial-tissue-embossed-blue-80": f"{base}/facial_tissues.jpg",
    "intimate-feminine-cleansing-wipes":     f"{base}/panty_liners.jpg",
    "organicup-menstrual-cup":               f"{base}/menstrual_cup.jpg",
    "lunette-menstrual-cup":                 f"{base}/menstrual_cup.jpg",
    "lactacyd-feminine-wash":                f"{base}/feminine_wash.jpg",
    "femfresh-intimate-wash":                f"{base}/feminine_wash.jpg",
}

for product in Product.objects.all():
    slug = product.slug
    image_path = None
    for key, path in IMAGE_MAP.items():
        if slug.startswith(key):
            image_path = path
            break
    if image_path:
        product.image = image_path
        product.save(update_fields=['image'])
        print(f"✅  {product.name[:60]} → {image_path.split('/')[-1]}")
    else:
        print(f"⚠️  No image match for: {slug}")

print("\nDone assigning images.")
