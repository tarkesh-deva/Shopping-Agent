import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Sheets configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Shopping List")

# Sheet column structure
SHEET_COLUMNS = {
    "ITEM_NAME": 0,
    "TARGET_PRICE": 1,
    "CURRENT_PRICE": 2,
    "URL": 3,
    "RETAILER": 4,
    "LAST_UPDATED": 5
}

# Twilio (WhatsApp) configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")

# Scheduler settings
UPDATE_INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", 30))
PRICE_DROP_THRESHOLD_PERCENT = float(os.getenv("PRICE_DROP_THRESHOLD_PERCENT", 5))

# Retailers to check
RETAILERS = [
    "amazon",
    "walmart",
    "flipkart",
    "myntra",
    "ajio"
]

# User agent for web scraping
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
