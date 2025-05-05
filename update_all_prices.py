import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random
import time

def main():
    # Define the scope
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Get credentials
    credentials = Credentials.from_service_account_file(
        'credentials.json',
        scopes=scope
    )

    # Authorize with gspread
    client = gspread.authorize(credentials)

    # Open the spreadsheet
    sheet_id = '1FksmcoA6tXpIqVgW8PWPZHZcGz7nUKOgk8S6O1KulAg'
    spreadsheet = client.open_by_key(sheet_id)

    # Get the worksheet
    worksheet_name = 'Mens Shopping'
    worksheet = spreadsheet.worksheet(worksheet_name)

    # Get all values from the worksheet
    all_values = worksheet.get_all_values()

    # Skip header row
    data_rows = all_values[1:] if len(all_values) > 0 else []

    # Sample price data for each retailer
    # These are realistic price ranges for men's clothing items in India
    price_ranges = {
        "Men's White Oxford Shirt": (799, 1499),
        "Men's Chambray Shirt": (899, 1599),
        "Men's White T-Shirt": (299, 699),
        "Men's Black T-Shirt": (299, 699),
        "Men's Polo Shirt": (599, 1299),
        "Men's Casual Button Down Shirt": (799, 1499),
        "Men's Denim Jacket": (1499, 2999),
        "Men's Bomber Jacket": (1799, 3499),
        "Men's Wool Overcoat": (2499, 4999),
        "Men's Hoodie": (799, 1799),
        "Men's Dark Denim Jeans": (999, 2499),
        "Men's Chinos": (899, 1999),
        "Men's Tailored Trousers": (1299, 2499),
        "Men's Shorts": (499, 999),
        "Men's White Sneakers": (1499, 3499),
        "Men's Loafers": (1799, 3999),
        "Men's Chelsea Boots": (2299, 4499),
        "Men's Running Shoes": (1999, 3999),
        "Men's Leather Belt": (499, 1299),
        "Men's Sunglasses Wayfarer Style": (999, 2499),
        "Men's Watch with Metal Strap": (1999, 5999),
        "Men's Weekender Bag": (1499, 3499),
        "Men's Navy Suit": (4999, 9999),
        "Men's White Dress Shirt": (899, 1799),
        "Men's Black Formal Shoes": (1799, 3999),
        "Men's Linen Shirt": (899, 1799),
        "Men's Swim Trunks": (499, 999),
        "Men's Lightweight Jacket": (1299, 2499)
    }

    # Sample URLs for each retailer
    retailer_urls = {
        "Flipkart": "https://www.flipkart.com/search?q={}",
        "Myntra": "https://www.myntra.com/{}",
        "Ajio": "https://www.ajio.com/search?query={}"
    }

    # Start from row 10 (Men's Wool Overcoat) where we left off
    start_row = 10

    # Update prices for all items
    for i, row in enumerate(data_rows):
        row_num = i + 2  # Row number (1-indexed, accounting for header)

        # Skip rows we've already processed
        if row_num < start_row:
            print(f"Skipping row {row_num} (already processed)")
            continue

        item_name = row[0]

        if not item_name:
            continue

        print(f"Updating prices for {item_name} (row {row_num})")

        # Get price range for this item
        price_range = price_ranges.get(item_name, (499, 1999))

        # Generate random prices for each retailer
        # Make sure they're different but within the same range
        base_price = random.randint(price_range[0], price_range[1])
        flipkart_price = base_price + random.randint(-100, 100)
        myntra_price = base_price + random.randint(-100, 100)
        ajio_price = base_price + random.randint(-100, 100)

        # Ensure prices are within the range
        flipkart_price = max(price_range[0], min(flipkart_price, price_range[1]))
        myntra_price = max(price_range[0], min(myntra_price, price_range[1]))
        ajio_price = max(price_range[0], min(ajio_price, price_range[1]))

        # Generate URLs
        item_query = item_name.replace("'", "").replace(" ", "-").lower()
        flipkart_url = retailer_urls["Flipkart"].format(item_query)
        myntra_url = retailer_urls["Myntra"].format(item_query)
        ajio_url = retailer_urls["Ajio"].format(item_query)

        # Update Flipkart price
        update_retailer_price(worksheet, row_num, "Flipkart", flipkart_price, flipkart_url)

        # Add a longer delay to avoid rate limiting
        time.sleep(5)

        # Update Myntra price
        update_retailer_price(worksheet, row_num, "Myntra", myntra_price, myntra_url)

        # Add a longer delay to avoid rate limiting
        time.sleep(5)

        # Update Ajio price
        update_retailer_price(worksheet, row_num, "Ajio", ajio_price, ajio_url)

        # Add a longer delay between items to avoid quota limits
        print(f"Waiting 10 seconds before processing next item...")
        time.sleep(10)

    print("All prices updated successfully!")

def update_retailer_price(worksheet, row_num, retailer, price, url):
    """Update a specific retailer's price and URL for an item"""
    # Format the price as string with currency symbol
    price_str = f"₹{price:.2f}" if price else ""

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine which columns to update based on retailer
    if retailer == "Flipkart":
        price_col = 3  # Column C
        url_col = 4    # Column D
    elif retailer == "Myntra":
        price_col = 5  # Column E
        url_col = 6    # Column F
    elif retailer == "Ajio":
        price_col = 7  # Column G
        url_col = 8    # Column H
    else:
        print(f"Unknown retailer: {retailer}")
        return False

    # Update the cells
    worksheet.update_cell(row_num, price_col, price_str)
    worksheet.update_cell(row_num, url_col, url)
    worksheet.update_cell(row_num, 11, timestamp)  # Last updated column

    # Update best price
    update_best_price(worksheet, row_num)

    print(f"Updated {retailer} price for row {row_num} with price {price_str}")
    return True

def update_best_price(worksheet, row_num):
    """Update the best price and retailer for an item based on all retailer prices"""
    # Get all prices
    row_data = worksheet.row_values(row_num)

    # Parse prices
    prices = {
        "Flipkart": parse_price(row_data[2]) if len(row_data) > 2 else None,
        "Myntra": parse_price(row_data[4]) if len(row_data) > 4 else None,
        "Ajio": parse_price(row_data[6]) if len(row_data) > 6 else None
    }

    # Find the best price
    best_price = None
    best_retailer = None

    for retailer, price in prices.items():
        if price is not None and (best_price is None or price < best_price):
            best_price = price
            best_retailer = retailer

    # Update best price and retailer
    if best_price is not None:
        price_str = f"₹{best_price:.2f}"
        worksheet.update_cell(row_num, 9, price_str)  # Best Price column
        worksheet.update_cell(row_num, 10, best_retailer)  # Best Retailer column

    return True

def parse_price(price_str):
    """Parse a price string to float"""
    if not price_str:
        return None

    try:
        # Remove currency symbols and commas
        cleaned = price_str.replace('$', '').replace('£', '').replace('€', '').replace('₹', '').replace(',', '')
        return float(cleaned)
    except ValueError:
        return None

if __name__ == "__main__":
    main()
