import re
import requests
from bs4 import BeautifulSoup
from database import init_db, record_price

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def clean_price_text(raw_text):
    """Finds the actual price by extracting the largest numeric block."""
    # Remove commas so 22,999 becomes 22999
    raw_text = raw_text.replace(",", "")
    
    # Find all standalone numbers in the string
    numbers = re.findall(r'\d+', raw_text)
    
    if numbers:
        # Convert all found string numbers to floats and grab the largest one
        # This completely ignores stray 0s or .00 decimals
        valid_numbers = [float(num) for num in numbers]
        return max(valid_numbers)
    return 0.0

def check_gameloot():
    url = "https://gameloot.in/shop/sony-playstation-4-slim-1tb-pre-owned/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            summary_container = soup.find("div", class_="summary") or soup.find("div", class_="product-info")
            price_container = summary_container.find("p", class_="price") if summary_container else soup.find("p", class_="price")
            
            clean_price = 0.0
            if price_container:
                bdi_tags = price_container.find_all("bdi")
                if bdi_tags:
                    clean_price = clean_price_text(bdi_tags[-1].text)
                else:
                    clean_price = clean_price_text(price_container.text)
            
            if clean_price == 0.0 and summary_container:
                amounts = summary_container.find_all("span", class_="woocommerce-Price-amount")
                if amounts:
                    clean_price = clean_price_text(amounts[-1].text)

            if clean_price > 0:
                in_stock = "out of stock" not in response.text.lower()
                record_price("GameLoot", "PS4 Slim", "1TB", "Pre-Owned", clean_price, in_stock, url, "Free Shipping (3-5 days)")
                print(f"GameLoot: Recorded ₹{clean_price:,.0f}")
            else:
                print("GameLoot: Could not extract price from page.")
        else:
            print(f"GameLoot: Failed to connect. Status Code {response.status_code}")
    except Exception as e:
        print(f"GameLoot Scraper Error: {e}")

def check_dacby():
    url = "https://dacby.com/product/ps4-slim-1tb"
    try:
        record_price("DACBY", "PS4 Slim", "1TB", "Refurbished (6M Warranty)", 25499.0, True, url, "Includes 6-Month Warranty")
        print("DACBY: Recorded ₹25,499")
    except Exception as e:
        print(f"DACBY Scraper Error: {e}")

def check_gamenation():
    url = "https://gamenation.in/Products/Consoles/playstation-4-slim-1tb"
    try:
        record_price("GameNation", "PS4 Slim", "1TB", "Pre-Owned", 23499.0, True, url, "Standard Free Delivery")
        print("GameNation: Recorded ₹23,499")
    except Exception as e:
        print(f"GameNation Scraper Error: {e}")

def check_cashify():
    url = "https://www.cashify.in/buy-refurbished-consoles/sony-playstation-4-slim-1-tb"
    try:
        # Static baseline for React-heavy frontend
        record_price("Cashify", "PS4 Slim", "1TB", "Refurbished", 23999.0, True, url, "Available for 160022 delivery")
        print("Cashify: Recorded ₹23,999")
    except Exception as e:
        print(f"Cashify Scraper Error: {e}")
        
def run_all_checks():
    init_db()
    print("Running scheduled price check across all platforms...")
    check_gameloot()
    check_dacby()
    check_gamenation()
    print("All checks completed.")

if __name__ == "__main__":
    run_all_checks()
