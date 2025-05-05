import gspread
from google.oauth2.service_account import Credentials

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
    
    # Fix missing names
    missing_names = {
        10: "Men's Wool Overcoat",
        11: "Men's Hoodie",
        12: "Men's Dark Denim Jeans",
        13: "Men's Chinos",
        14: "Men's Tailored Trousers",
        15: "Men's Shorts"
    }
    
    # Update missing names
    for row_num, name in missing_names.items():
        worksheet.update_cell(row_num, 1, name)
        print(f"Fixed row {row_num}: {name}")
    
    print("Fixed all missing names!")

if __name__ == "__main__":
    main()
