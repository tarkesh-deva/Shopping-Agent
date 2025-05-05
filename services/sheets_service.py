import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from loguru import logger

import config

class GoogleSheetsService:
    """Service for interacting with Google Sheets"""

    def __init__(self):
        """Initialize the Google Sheets service"""
        try:
            # Define the scope
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Get credentials
            credentials_path = os.path.abspath(config.GOOGLE_SHEETS_CREDENTIALS_FILE)
            credentials = Credentials.from_service_account_file(
                credentials_path,
                scopes=scope
            )

            # Authorize with gspread
            self.client = gspread.authorize(credentials)

            # Open the spreadsheet
            self.sheet_id = config.GOOGLE_SHEET_ID
            self.spreadsheet = self.client.open_by_key(self.sheet_id)

            # Get the specific worksheet
            self.worksheet = self.spreadsheet.worksheet(config.GOOGLE_SHEET_NAME)

            logger.info(f"Connected to Google Sheet: {self.spreadsheet.title}")
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{config.GOOGLE_SHEET_NAME}' not found in the Google Sheet. Please create this worksheet or update GOOGLE_SHEET_NAME in .env")
            raise Exception(f"Worksheet '{config.GOOGLE_SHEET_NAME}' not found")
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet with ID '{config.GOOGLE_SHEET_ID}' not found. Please check GOOGLE_SHEET_ID in .env")
            raise Exception(f"Spreadsheet with ID '{config.GOOGLE_SHEET_ID}' not found")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
            raise

    def get_all_items(self):
        """Get all items from the shopping list"""
        try:
            # Get all values from the worksheet
            all_values = self.worksheet.get_all_values()

            # Skip header row
            data_rows = all_values[1:] if len(all_values) > 0 else []

            # Convert to list of dictionaries
            items = []
            for i, row in enumerate(data_rows):
                if len(row) >= 2:  # Ensure row has at least name and target price
                    # Get the best price and retailer
                    best_price = None
                    best_retailer = None
                    best_url = ""

                    # Check Flipkart price (column 2)
                    flipkart_price = self._parse_price(row[2]) if len(row) > 2 and row[2] else None
                    if flipkart_price and (best_price is None or flipkart_price < best_price):
                        best_price = flipkart_price
                        best_retailer = "Flipkart"
                        best_url = row[3] if len(row) > 3 else ""

                    # Check Myntra price (column 4)
                    myntra_price = self._parse_price(row[4]) if len(row) > 4 and row[4] else None
                    if myntra_price and (best_price is None or myntra_price < best_price):
                        best_price = myntra_price
                        best_retailer = "Myntra"
                        best_url = row[5] if len(row) > 5 else ""

                    # Check Ajio price (column 6)
                    ajio_price = self._parse_price(row[6]) if len(row) > 6 and row[6] else None
                    if ajio_price and (best_price is None or ajio_price < best_price):
                        best_price = ajio_price
                        best_retailer = "Ajio"
                        best_url = row[7] if len(row) > 7 else ""

                    # Use the best price from the sheet if available (column 8)
                    sheet_best_price = self._parse_price(row[8]) if len(row) > 8 and row[8] else None
                    sheet_best_retailer = row[9] if len(row) > 9 and row[9] else None

                    if sheet_best_price:
                        best_price = sheet_best_price
                        best_retailer = sheet_best_retailer

                    # Add the item to the list
                    items.append({
                        "id": i + 2,  # Row number (1-indexed, accounting for header)
                        "name": row[0],  # Item Name
                        "target_price": self._parse_price(row[1]),  # Target Price
                        "current_price": best_price,  # Best Price
                        "url": best_url,  # URL of the best price
                        "retailer": best_retailer,  # Retailer with the best price
                        "last_updated": row[10] if len(row) > 10 else ""  # Last Updated
                    })

            return items
        except Exception as e:
            logger.error(f"Failed to get items from Google Sheet: {e}")
            raise

    def get_item(self, item_id):
        """Get a specific item by its ID (row number)"""
        try:
            # Convert item_id to integer
            row_num = int(item_id)

            # Get the row
            row = self.worksheet.row_values(row_num)

            # Convert to dictionary
            if len(row) >= 2:  # Ensure row has at least name and target price
                # Get the best price and retailer
                best_price = None
                best_retailer = None
                best_url = ""

                # Check Flipkart price (column 2)
                flipkart_price = self._parse_price(row[2]) if len(row) > 2 and row[2] else None
                if flipkart_price and (best_price is None or flipkart_price < best_price):
                    best_price = flipkart_price
                    best_retailer = "Flipkart"
                    best_url = row[3] if len(row) > 3 else ""

                # Check Myntra price (column 4)
                myntra_price = self._parse_price(row[4]) if len(row) > 4 and row[4] else None
                if myntra_price and (best_price is None or myntra_price < best_price):
                    best_price = myntra_price
                    best_retailer = "Myntra"
                    best_url = row[5] if len(row) > 5 else ""

                # Check Ajio price (column 6)
                ajio_price = self._parse_price(row[6]) if len(row) > 6 and row[6] else None
                if ajio_price and (best_price is None or ajio_price < best_price):
                    best_price = ajio_price
                    best_retailer = "Ajio"
                    best_url = row[7] if len(row) > 7 else ""

                # Use the best price from the sheet if available (column 8)
                sheet_best_price = self._parse_price(row[8]) if len(row) > 8 and row[8] else None
                sheet_best_retailer = row[9] if len(row) > 9 and row[9] else None

                if sheet_best_price:
                    best_price = sheet_best_price
                    best_retailer = sheet_best_retailer

                return {
                    "id": row_num,
                    "name": row[0],  # Item Name
                    "target_price": self._parse_price(row[1]),  # Target Price
                    "current_price": best_price,  # Best Price
                    "url": best_url,  # URL of the best price
                    "retailer": best_retailer,  # Retailer with the best price
                    "last_updated": row[10] if len(row) > 10 else ""  # Last Updated
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get item {item_id} from Google Sheet: {e}")
            raise

    def update_item_price(self, row_num, price, url, retailer):
        """Update an item's price, URL, and retailer"""
        try:
            # Format the price as string with currency symbol
            price_str = f"${price:.2f}" if price else ""

            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update the cells
            self.worksheet.update_cell(row_num, config.SHEET_COLUMNS["CURRENT_PRICE"] + 1, price_str)
            self.worksheet.update_cell(row_num, config.SHEET_COLUMNS["URL"] + 1, url)
            self.worksheet.update_cell(row_num, config.SHEET_COLUMNS["RETAILER"] + 1, retailer)
            self.worksheet.update_cell(row_num, config.SHEET_COLUMNS["LAST_UPDATED"] + 1, timestamp)

            logger.info(f"Updated item in row {row_num} with price {price_str} from {retailer}")
            return True
        except Exception as e:
            logger.error(f"Failed to update item in row {row_num}: {e}")
            raise

    def check_for_price_drops(self):
        """Check for price drops and return items with significant drops"""
        try:
            items = self.get_all_items()
            price_drops = []

            for item in items:
                # Skip items without prices
                if not item["current_price"] or not item["target_price"]:
                    continue

                # Calculate price drop percentage
                if item["current_price"] < item["target_price"]:
                    drop_percent = (item["target_price"] - item["current_price"]) / item["target_price"] * 100

                    # Check if drop exceeds threshold
                    if drop_percent >= config.PRICE_DROP_THRESHOLD_PERCENT:
                        price_drops.append(item)

            return price_drops
        except Exception as e:
            logger.error(f"Failed to check for price drops: {e}")
            raise

    def _parse_price(self, price_str):
        """Parse a price string to float"""
        if not price_str:
            return None

        try:
            # Remove currency symbols and commas
            cleaned = price_str.replace('$', '').replace('£', '').replace('€', '').replace('₹', '').replace(',', '')
            return float(cleaned)
        except ValueError:
            return None

    def create_shopping_worksheet(self, worksheet_name="Mens Shopping"):
        """Create a new worksheet with the proper columns for the shopping assistant"""
        try:
            # Check if worksheet already exists
            try:
                existing_worksheet = self.spreadsheet.worksheet(worksheet_name)
                logger.info(f"Worksheet '{worksheet_name}' already exists")
                return existing_worksheet
            except gspread.exceptions.WorksheetNotFound:
                # Create new worksheet
                new_worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
                logger.info(f"Created new worksheet: {worksheet_name}")

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
                new_worksheet.update('A1:K1', [headers])

                # Format header row
                header_format = {
                    "textFormat": {"bold": True},
                    "horizontalAlignment": "CENTER",
                    "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
                }

                # Apply formatting to header row
                format_range = f'A1:K1'
                new_worksheet.format(format_range, header_format)

                # Resize columns to fit content
                for i in range(1, len(headers) + 1):
                    new_worksheet.columns_auto_resize(i - 1, i)

                return new_worksheet
        except Exception as e:
            logger.error(f"Failed to create worksheet '{worksheet_name}': {e}")
            raise

    def update_retailer_price(self, worksheet, row_num, retailer, price, url):
        """Update a specific retailer's price and URL for an item"""
        try:
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
                logger.warning(f"Unknown retailer: {retailer}")
                return False

            # Update the cells
            worksheet.update_cell(row_num, price_col, price_str)
            worksheet.update_cell(row_num, url_col, url)
            worksheet.update_cell(row_num, 11, timestamp)  # Last updated column

            # Check if this is the new best price
            self._update_best_price(worksheet, row_num)

            logger.info(f"Updated {retailer} price for item in row {row_num} with price {price_str}")
            return True
        except Exception as e:
            logger.error(f"Failed to update {retailer} price for item in row {row_num}: {e}")
            raise

    def _update_best_price(self, worksheet, row_num):
        """Update the best price and retailer for an item based on all retailer prices"""
        try:
            # Get all prices
            row_data = worksheet.row_values(row_num)

            # Parse prices
            prices = {
                "Flipkart": self._parse_price(row_data[2]) if len(row_data) > 2 else None,
                "Myntra": self._parse_price(row_data[4]) if len(row_data) > 4 else None,
                "Ajio": self._parse_price(row_data[6]) if len(row_data) > 6 else None
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
        except Exception as e:
            logger.error(f"Failed to update best price for item in row {row_num}: {e}")
            raise
