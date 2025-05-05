import gspread
from google.oauth2.service_account import Credentials
import sys

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
    
    # Print available worksheets
    print('Available worksheets:', [ws.title for ws in spreadsheet.worksheets()])
    
    # Create a new worksheet if it doesn't exist
    worksheet_name = 'Shopping Assistant'
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        print(f"Worksheet '{worksheet_name}' already exists")
    except gspread.exceptions.WorksheetNotFound:
        # Create new worksheet
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
        print(f"Created new worksheet: {worksheet_name}")
    
    # Set up header row
    headers = [
        "Item Name",
        "Target Price (₹)",
        "Flipkart Price (₹)",
        "Flipkart URL",
        "Myntra Price (₹)",
        "Myntra URL",
        "Ajio Price (₹)",
        "Ajio URL",
        "Best Price (₹)",
        "Best Retailer",
        "Last Updated"
    ]
    
    # Update header row
    worksheet.update('A1:K1', [headers])
    
    # Format header row
    header_format = {
        "textFormat": {"bold": True},
        "horizontalAlignment": "CENTER",
        "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
    }
    
    # Apply formatting to header row
    format_range = f'A1:K1'
    worksheet.format(format_range, header_format)
    
    # Resize columns to fit content
    for i in range(1, len(headers) + 1):
        worksheet.columns_auto_resize(i - 1, i)
    
    print("Worksheet setup complete!")

if __name__ == "__main__":
    main()
