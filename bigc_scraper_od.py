import bs4
import requests
import pandas as pd
import time
import random
import re
import os
from datetime import datetime

# --- CATEGORY & MAPPING SETUP ---

url_mappings = {
    "https://www.bigc.co.th/category/men-skincare": ("men", "skincare"),
    "https://www.bigc.co.th/category/men-facial-cleanser": ("men", "facial-cleanser"),
    "https://www.bigc.co.th/category/men-cologne": ("men", "cologne"),
    "https://www.bigc.co.th/category/men-shaving-grooming": ("men", "shaving-grooming"),

    "https://www.bigc.co.th/category/facial-cream-serum": ("facial", "cream-serum"),
    "https://www.bigc.co.th/category/facial-sunscreen": ("facial", "sunscreen"),
    "https://www.bigc.co.th/category/toner-mist": ("facial", "toner-mist"),
    "https://www.bigc.co.th/category/facial-mask-acne-gel": ("facial", "mask-acne-gel"),
    "https://www.bigc.co.th/category/other-facial-skincare": ("facial", "other-facial-skincare"),
    "https://www.bigc.co.th/category/blotting-paper": ("facial", "blotting-paper"),
    "https://www.bigc.co.th/category/acne-patch": ("facial", "acne-patch"),

    "https://www.bigc.co.th/category/body-wash-shower-gel": ("body", "wash-shower-gel"),
    "https://www.bigc.co.th/category/body-scrub": ("body", "scrub"),
    "https://www.bigc.co.th/category/body-lotion-cream-oil": ("body", "lotion-cream-oil"),
    "https://www.bigc.co.th/category/body-spray-deodorant-perfume": ("body", "spray-deodorant-perfume"),
    "https://www.bigc.co.th/category/body-powder": ("body", "powder"),
    "https://www.bigc.co.th/category/feminine-care": ("body", "feminine-care"),
    "https://www.bigc.co.th/category/hair-removal-shave": ("body", "hair-removal-shave"),

    "https://www.bigc.co.th/category/shampoo-conditioner-hair-treatment": ("hair", "shampoo-conditioner-hair-treatment"),
    "https://www.bigc.co.th/category/hair-color": ("hair", "color"),
    "https://www.bigc.co.th/category/hair-straightening-treatment": ("hair", "straightening-treatment"),
    "https://www.bigc.co.th/category/hair-styling": ("hair", "styling"),

    "https://www.bigc.co.th/category/toothpaste": ("oral-care", "toothpaste"),
    "https://www.bigc.co.th/category/toothbrush": ("oral-care", "toothbrush"),
    "https://www.bigc.co.th/category/mouthwash-mouthspray": ("oral-care", "mouthwash-mouthspray"),
    "https://www.bigc.co.th/category/dental-floss": ("oral-care", "dental-floss"),
    "https://www.bigc.co.th/category/other-oral-care": ("oral-care", "other-oral-care"),

    "https://www.bigc.co.th/category/makeup-remover": ("make-up", "makeup-remover"),
    "https://www.bigc.co.th/category/face-makeup": ("make-up", "face-makeup"),
    "https://www.bigc.co.th/category/eye-makeup": ("make-up", "eye-makeup"),
    "https://www.bigc.co.th/category/lip-makeup": ("make-up", "lip-makeup"),
    "https://www.bigc.co.th/category/hand-foot-body-care": ("make-up", "hand-foot-body-care"),
    "https://www.bigc.co.th/category/nail-polish-remover": ("make-up", "nail-polish-remover"),
    "https://www.bigc.co.th/category/makeup-accessories": ("make-up", "makeup-accessories"),
    "https://www.bigc.co.th/category/cotton-buds-balls-pads": ("make-up", "cotton-buds-balls-pads"),

    "https://www.bigc.co.th/category/sanitary-pads-tampons": ("sanitary", "sanitary-pads-tampons"),
}

badge_map = {
    "1661938166395": "2 ชิ้นถูกกว่า",
    "1678349698676": "ราคาพิเศษ",
    "1661938480187": "1 แถม 1",
    "1689932276174": "6 แถม 1",
    "1661938612902": "2 แถม 1"
}

# --- SCRAPER FUNCTION ---

def scrape_bigc(url, category, subcategory):
    print(f"🔍 Scraping: {category} / {subcategory}")
    product_data = []
    today_str = datetime.today().strftime("%Y-%m-%d")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }

    for page in range(1, 51):
        page_url = f"{url}?limit=100&page={page}"
        try:
            res = requests.get(page_url, headers=headers, timeout=10)
            if res.status_code != 200:
                break

            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('div', class_='category_result_col__LmuH8')
            if not cards:
                break

            for card in cards:
                try:
                    # Image + Barcode
                    img = card.find('div', class_='productCard_img_dp__8bHIe').find('img')
                    image_url = img['src'] if img else None
                    barcode_match = re.search(r'(\d{8,14})', image_url) if image_url else None
                    barcode = barcode_match.group(1) if barcode_match else None

                    # Name
                    name_tag = card.find('div', class_='productCard_title__f1ohZ').find('a')
                    name = name_tag.text.strip() if name_tag else None

                    # Price
                    current = card.find('span', class_='productCard_sale_price___gDpF')
                    base = card.find('div', class_='productCard_base_price__2GuG3')
                    current_price = current.text.strip().replace("฿", "") if current else None
                    base_price = base.text.strip().replace("฿", "") if base else None

                    # Mechanics from badge
                    badge_div = card.find('div', class_='productCard_badge_top-right__cvOLY')
                    badge_src = badge_div.find('img')['src'] if badge_div else None
                    badge_id = re.search(r'(\d{13})\.png', badge_src).group(1) if badge_src else None
                    mechanics = badge_map.get(badge_id, "CHECK" if badge_id else None)

                    product_data.append({
                        "Date": today_str,
                        "Category": category,
                        "Subcategory": subcategory,
                        "Barcode": barcode,
                        "Product_Name": name,
                        "Base_Price": base_price,
                        "Current_Price": current_price,
                        "Mechanics": mechanics,
                        "Image_URL": image_url
                    })
                except Exception as e:
                    print(f"❌ Card error: {e}")
                    continue

            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"❌ Page error: {e}")
            continue

    return product_data

# --- SIZE AND PACK EXTRACTION ---

def extract_size_and_pack(name):
    if not name:
        return None, None

    # Size: match units like มล., กรัม, ซม., กก.
    size_match = re.search(r"(\d+[\.,]?\d*\s?(มล\.|กรัม|ก\.|กก\.|ซม\.))", name)
    size = size_match.group(0).strip() if size_match else None

    # Pack: match patterns like แพ็ค 4, 14 ชิ้น, 6 แผ่น
    pack_match = re.search(r"(แพ็ค\s*\d+|แพค\s*\d+|\d+\s*(ชิ้น|แผ่น))", name)
    pack = pack_match.group(0).strip() if pack_match else None

    return size, pack

# --- RUN SCRAPER ---

all_products = []
for url, (cat, subcat) in url_mappings.items():
    try:
        results = scrape_bigc(url, cat, subcat)
        all_products.extend(results)
    except Exception as e:
        print(f"❌ Failed on {url}: {e}")

df = pd.DataFrame(all_products)

# --- DEFINE PATHS FOR ONEDRIVE SYNC ---

onedrive_root = r"C:\Users\kritin.kay\OneDrive - CJ Express Group Co.,Ltd\automation-scraper"
daily_folder = os.path.join(onedrive_root, "Daily Price")
master_folder = os.path.join(onedrive_root, "Product Master")

# Ensure folders exist
os.makedirs(daily_folder, exist_ok=True)
os.makedirs(master_folder, exist_ok=True)

# --- SAVE DAILY PRICE FILE ---
date_str = datetime.today().strftime("%Y%m%d")
daily_filename = f"{date_str}_BigC_Products.xlsx"
daily_path = os.path.join(daily_folder, daily_filename)

daily_df = df[[
    "Date", "Category", "Subcategory", "Barcode",
    "Product_Name", "Base_Price", "Current_Price", "Mechanics"
]]

daily_df.to_excel(daily_path, index=False)
print(f"✅ Daily price saved to OneDrive: {daily_path}")

# --- SAVE MASTER FILE ---
master_df = df[["Barcode", "Product_Name", "Image_URL"]].dropna(subset=["Barcode"])
master_df = master_df.drop_duplicates(subset="Barcode", keep="first")

# Extract size and pack
master_df[["Size", "Pack"]] = master_df["Product_Name"].apply(
    lambda x: pd.Series(extract_size_and_pack(x))
)

master_path = os.path.join(master_folder, "Product_Master_BigC.xlsx")
master_df.to_excel(master_path, index=False)
print(f"✅ Master file saved to OneDrive: {master_path}")
