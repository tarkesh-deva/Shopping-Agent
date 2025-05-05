# Shopping Assistant MCP Server

A Master Control Program (MCP) server that monitors a Google Sheets shopping list, finds the best deals from various online retailers, and sends WhatsApp notifications for price drops.

## Features

- Google Sheets integration for tracking shopping items
- Automated price checking from multiple retailers (Amazon, Walmart, Flipkart, Myntra, Ajio)
- Best deal finder with links to purchase
- WhatsApp notifications for price drops
- Scheduled updates to keep prices current

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
- Target Price
- Current Best Price
- Best Price URL
- Best Price Retailer
- Last Updated

## Configuration

Edit `config.py` to customize:
- Update frequency
- Retailers to check
- Notification preferences
- Price threshold for alerts

## License

MIT
