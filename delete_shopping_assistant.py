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
    
    # Print available worksheets
    print('Available worksheets:', [ws.title for ws in spreadsheet.worksheets()])
    
    # Delete the Shopping Assistant worksheet if it exists
    try:
        worksheet = spreadsheet.worksheet('Shopping Assistant')
        spreadsheet.del_worksheet(worksheet)
        print("Deleted 'Shopping Assistant' worksheet")
    except gspread.exceptions.WorksheetNotFound:
        print("'Shopping Assistant' worksheet not found")
    
    # Print available worksheets after deletion
    print('Available worksheets after deletion:', [ws.title for ws in spreadsheet.worksheets()])

if __name__ == "__main__":
    main()
