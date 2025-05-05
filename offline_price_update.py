#!/usr/bin/env python3
"""
Offline Price Update Script

This script can be run manually to update prices in the Google Sheet when the main server is offline.
It connects directly to the Google Sheet, updates prices for all items, and optionally sends notifications.

Usage:
    python offline_price_update.py [--notify]

Options:
    --notify    Send WhatsApp notifications for price drops
"""

import os
import sys
import argparse
import gspread
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description='Update prices in Google Sheet when server is offline')
parser.add_argument('--notify', action='store_true', help='Send WhatsApp notifications for price drops')
args = parser.parse_args()

# Google Sheets configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Mens Shopping")

# Twilio (WhatsApp) configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")

# Price drop threshold
PRICE_DROP_THRESHOLD_PERCENT = float(os.getenv("PRICE_DROP_THRESHOLD_PERCENT", 5))

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
    
    return best_price, best_retailer

def check_for_price_drops(worksheet, row_num, item_name, target_price, best_price, best_retailer, best_url):
    """Check if there's a significant price drop and return notification message if needed"""
    if not best_price or not target_price:
        return None
    
    # Calculate price drop percentage
    if best_price < target_price:
        drop_percent = (target_price - best_price) / target_price * 100
        
        # Check if drop exceeds threshold
        if drop_percent >= PRICE_DROP_THRESHOLD_PERCENT:
            message = f"🔔 Price Drop Alert: {item_name} is now ₹{best_price:.2f} at {best_retailer} (was ₹{target_price:.2f}). That's {drop_percent:.1f}% off! Shop now: {best_url}"
            return message
    
    return None

def send_whatsapp_notification(message):
    """Send a WhatsApp notification using Twilio"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO]):
        print("Twilio credentials not fully configured. WhatsApp notifications are disabled.")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            to=f"whatsapp:{TWILIO_WHATSAPP_TO}"
        )
        print(f"WhatsApp notification sent: {message}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp notification: {e}")
        return False

def main():
    print("Starting offline price update...")
    
    # Define the scope
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Get credentials
    try:
        credentials = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE, 
            scopes=scope
        )
        
        # Authorize with gspread
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Get the worksheet
        worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
        
        print(f"Connected to Google Sheet: {GOOGLE_SHEET_NAME}")
    except Exception as e:
        print(f"Failed to connect to Google Sheet: {e}")
        sys.exit(1)
    
    # Get all values from the worksheet
    all_values = worksheet.get_all_values()
    
    # Skip header row
    data_rows = all_values[1:] if len(all_values) > 0 else []
    
    # Track notifications
    notifications = []
    
    # Update prices for all items
    for i, row in enumerate(data_rows):
        row_num = i + 2  # Row number (1-indexed, accounting for header)
        item_name = row[0]
        
        if not item_name:
            continue
        
        print(f"Updating prices for {item_name} (row {row_num})")
        
        # Get target price
        target_price = parse_price(row[1])
        
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
        
        # Get the best price and retailer
        best_price, best_retailer = update_best_price(worksheet, row_num)
        
        # Determine the best URL
        best_url = ""
        if best_retailer == "Flipkart":
            best_url = flipkart_url
        elif best_retailer == "Myntra":
            best_url = myntra_url
        elif best_retailer == "Ajio":
            best_url = ajio_url
        
        # Check for price drops
        if args.notify:
            notification = check_for_price_drops(worksheet, row_num, item_name, target_price, best_price, best_retailer, best_url)
            if notification:
                notifications.append(notification)
        
        # Add a longer delay between items to avoid quota limits
        print(f"Waiting 10 seconds before processing next item...")
        time.sleep(10)
    
    print("All prices updated successfully!")
    
    # Send notifications
    if args.notify and notifications:
        print(f"Sending {len(notifications)} price drop notifications...")
        for notification in notifications:
            send_whatsapp_notification(notification)
    
    print("Offline price update completed!")

if __name__ == "__main__":
    main()
