import gspread
from google.oauth2.service_account import Credentials
import json

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
    
    # Load men's items from JSON file
    with open('mens_items.json', 'r') as f:
        items = json.load(f)
    
    # Get existing items to avoid duplicates
    all_values = worksheet.get_all_values()
    existing_items = [row[0] for row in all_values[1:] if row and len(row) > 0]
    
    # Prepare batch update
    batch_data = []
    next_row = len(all_values) + 1
    
    # Add new items
    added_count = 0
    for item in items:
        item_name = item['name']
        if item_name not in existing_items:
            # Format target price
            target_price_str = f"₹{item['target_price']:.2f}" if 'target_price' in item else ""
            
            # Add to batch update
            batch_data.append({
                'range': f'A{next_row}:B{next_row}',
                'values': [[item_name, target_price_str]]
            })
            
            next_row += 1
            added_count += 1
    
    # Execute batch update if there are items to add
    if batch_data:
        worksheet.batch_update(batch_data)
        print(f"Added {added_count} new items to the worksheet")
    else:
        print("No new items to add")

if __name__ == "__main__":
    main()
