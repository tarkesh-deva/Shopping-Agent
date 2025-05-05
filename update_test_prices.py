import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

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
    
    # Test data for a few items
    test_data = [
        {
            "row": 2,  # Men's White Oxford Shirt
            "retailer": "Flipkart",
            "price": 999.00,
            "url": "https://www.flipkart.com/example-oxford-shirt"
        },
        {
            "row": 3,  # Men's Chambray Shirt
            "retailer": "Myntra",
            "price": 899.00,
            "url": "https://www.myntra.com/example-chambray-shirt"
        },
        {
            "row": 4,  # Men's White T-Shirt
            "retailer": "Ajio",
            "price": 449.00,
            "url": "https://www.ajio.com/example-white-tshirt"
        },
        {
            "row": 5,  # Men's Black T-Shirt
            "retailer": "Flipkart",
            "price": 399.00,
            "url": "https://www.flipkart.com/example-black-tshirt"
        },
        {
            "row": 8,  # Men's Denim Jacket
            "retailer": "Myntra",
            "price": 1799.00,
            "url": "https://www.myntra.com/example-denim-jacket"
        }
    ]
    
    # Update prices for test items
    for item in test_data:
        update_retailer_price(worksheet, item["row"], item["retailer"], item["price"], item["url"])
        print(f"Updated {item['retailer']} price for row {item['row']} with price ₹{item['price']:.2f}")
    
    print("Test price updates completed!")

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
