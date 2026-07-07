#!/usr/bin/env python
import os
import sys
import django
import requests
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from shop.models import Product

# Mapping categories to keywords
keyword_map = {
    'phones-tablets': 'smartphone,phone',
    'laptops-computers': 'laptop,computer',
    'tvs-audio': 'tv,television',
    'kitchen-appliances': 'blender,cooker',
    'home-appliances': 'refrigerator,washing-machine',
    'womens-fashion': 'dress,clothing',
    'mens-fashion': 'shirt,suit',
    'shoes-sneakers': 'sneakers,shoes',
    'skincare': 'skincare,lotion',
    'makeup': 'makeup,lipstick',
    'exercise-fitness': 'dumbbell,yoga-mat',
    'toys-games': 'toys,lego',
    'menstrual-products': 'menstrual,pads',
    'wellness-kits': 'wellness,essential-oil',
    'books-education': 'books,novel',
    'stationery': 'stationery,notebook',
    'gaming': 'gamepad,console',
}

# Generic fallback keywords based on product name
def get_keyword(product):
    cat_slug = product.category.slug
    name_lower = product.name.lower()
    
    # Check specific names first
    if 'samsung' in name_lower and 'tv' in name_lower:
        return 'television'
    if 'iphone' in name_lower:
        return 'iphone'
    if 'galaxy' in name_lower:
        return 'galaxy-phone'
    if 'dumbbell' in name_lower:
        return 'dumbbell'
    if 'yoga' in name_lower:
        return 'yoga-mat'
    if 'cup' in name_lower and 'menstrual' in name_lower:
        return 'menstrual-cup'
    if 'pads' in name_lower:
        return 'sanitary-pad'
    if 'underwear' in name_lower:
        return 'underwear'
    if 'LEGO' in product.name:
        return 'lego'
    if 'dress' in name_lower:
        return 'dress'
    if 'chair' in name_lower:
        return 'office-chair'
    if 'paper' in name_lower:
        return 'a4-paper'
    if 'controller' in name_lower or 'dualsense' in name_lower:
        return 'game-controller'
    if 'headset' in name_lower:
        return 'gaming-headset'
    
    # Fallback to category map
    return keyword_map.get(cat_slug, 'product')

media_dir = '/var/www/venv/myshop/media/products/2026/06/28'
os.makedirs(media_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

products = Product.objects.all()
print(f"Starting to download images for {products.count()} products...")

success_count = 0
skip_count = 0

for i, p in enumerate(products, 1):
    # Check if product already has a valid local file
    if p.image and os.path.exists(os.path.join('/var/www/venv/myshop/media', p.image.name)):
        print(f"[{i}/{products.count()}] Skipping {p.name} - Image already exists.")
        skip_count += 1
        continue
        
    keyword = get_keyword(p)
    # Using loremflickr as a highly reliable stock image query provider
    url = f"https://loremflickr.com/600/600/{keyword}"
    
    filename = f"{slugify(p.name)}.jpg"
    filepath = os.path.join(media_dir, filename)
    db_path = f"products/2026/06/28/{filename}"
    
    print(f"[{i}/{products.count()}] Downloading image for {p.name} using keyword: '{keyword}'...")
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            p.image = db_path
            p.save()
            print(f"   ✓ Saved to {db_path}")
            success_count += 1
        else:
            print(f"   ✗ Failed (Status: {r.status_code})")
    except Exception as e:
        print(f"   ✗ Error: {e}")

print(f"\nFinished! Downloads: {success_count}, Skipped: {skip_count}")
