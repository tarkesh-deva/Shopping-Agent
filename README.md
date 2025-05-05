# Men's Shopping Assistant

A shopping assistant that monitors a Google Sheets shopping list for men's clothing items, finds the best deals from various Indian online retailers (Flipkart, Myntra, Ajio), and sends WhatsApp notifications for price drops.

## Features

- Google Sheets integration for tracking men's clothing items
- Automated price checking from multiple Indian retailers (Flipkart, Myntra, Ajio)
- Best deal finder with links to purchase
- WhatsApp notifications for price drops
- Scheduled updates every 12 hours to keep prices current
- Offline price update capability when server is unavailable

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up Google Sheets API:
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create OAuth credentials
   - Download credentials as `credentials.json` and place in project root

4. Set up Twilio for WhatsApp notifications:
   - Create a Twilio account
   - Set up WhatsApp sandbox or Business API

5. Create a `.env` file based on `.env.example` with your credentials

6. Run the server:
   ```
   uvicorn app:app --reload
   ```

## Google Sheets Format

Your Google Sheets should have the following columns:
- Item Name
- Target Price (₹)
- Flipkart Price (₹)
- Flipkart URL
- Myntra Price (₹)
- Myntra URL
- Ajio Price (₹)
- Ajio URL
- Best Price (₹)
- Best Retailer
- Last Updated

## Configuration

Edit `.env` file to customize:
- Update frequency (default: every 12 hours)
- Price threshold for alerts (default: 5%)
- WhatsApp notification settings
- Google Sheets connection details

## Offline Price Updates

When the server is offline, you can still update prices using the offline script:

```bash
# Update prices without notifications
python offline_price_update.py

# Update prices and send WhatsApp notifications for price drops
python offline_price_update.py --notify
```

This script connects directly to Google Sheets and updates prices for all items in your shopping list. It can be run manually or scheduled using cron jobs.

### Setting up a Cron Job for Offline Updates

To schedule the offline price update script to run automatically at 11 AM and 8 PM IST, you can use the provided setup script:

```bash
# Make the script executable
chmod +x setup_cron.sh

# Run the setup script
./setup_cron.sh
```

This will add cron jobs to run the price update script twice daily. You can verify the cron jobs with:

```bash
crontab -l
```

The output should show something like:

```
# Shopping Assistant price update jobs
0 11 * * * cd /path/to/shopping-assistant && source venv/bin/activate && python offline_price_update.py --notify # Run at 11 AM IST
0 20 * * * cd /path/to/shopping-assistant && source venv/bin/activate && python offline_price_update.py --notify # Run at 8 PM IST
```

## License

MIT
