import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Import services
from services.sheets_service import GoogleSheetsService
from services.whatsapp_service import WhatsAppService
from services.scheduler import Scheduler
from agents.price_comparator import PriceComparator
from agents.indian_price_comparator import IndianPriceComparator

# Define models
class Item(BaseModel):
    name: str
    target_price: Optional[float] = None

# Create FastAPI app
app = FastAPI(
    title="Shopping Assistant MCP Server",
    description="Monitors Google Sheets shopping list and finds the best deals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
sheets_service = None
whatsapp_service = None
price_comparator = None
indian_price_comparator = None
scheduler = None

try:
    sheets_service = GoogleSheetsService()
    whatsapp_service = WhatsAppService()
    price_comparator = PriceComparator()
    indian_price_comparator = IndianPriceComparator()
    scheduler = Scheduler(sheets_service, price_comparator, whatsapp_service)
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    # We'll continue and let the endpoints handle errors

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts"""
    try:
        # Create the Shopping Assistant worksheet if it doesn't exist
        if sheets_service:
            try:
                sheets_service.create_shopping_worksheet()
                logger.info("Shopping Assistant worksheet created or already exists")
            except Exception as e:
                logger.error(f"Failed to create Shopping Assistant worksheet: {e}")

        # Start the scheduler
        if scheduler:
            scheduler.start()
            logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when the application shuts down"""
    try:
        scheduler.stop()
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")

@app.get("/")
async def root():
    """Root endpoint to check if the server is running"""
    return {"status": "online", "message": "Shopping Assistant MCP Server is running"}

@app.get("/items")
async def get_items():
    """Get all items from the shopping list"""
    try:
        items = sheets_service.get_all_items()
        return {"items": items}
    except Exception as e:
        logger.error(f"Failed to get items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-prices")
async def update_prices(background_tasks: BackgroundTasks):
    """Manually trigger a price update"""
    try:
        background_tasks.add_task(scheduler.update_prices)
        return {"status": "success", "message": "Price update started in background"}
    except Exception as e:
        logger.error(f"Failed to start price update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notify/{item_id}")
async def send_notification(item_id: str):
    """Manually send a notification for a specific item"""
    try:
        item = sheets_service.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        message = f"🔔 Price Alert: {item['name']} is now available for {item['current_price']} at {item['retailer']}. Shop now: {item['url']}"
        whatsapp_service.send_message(message)
        return {"status": "success", "message": "Notification sent"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-shopping-assistant")
async def create_shopping_assistant():
    """Create a new Shopping Assistant worksheet"""
    try:
        if not sheets_service:
            raise HTTPException(status_code=500, detail="Google Sheets service not initialized")

        worksheet = sheets_service.create_shopping_worksheet()
        return {"status": "success", "message": f"Created Shopping Assistant worksheet"}
    except Exception as e:
        logger.error(f"Failed to create Shopping Assistant worksheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-items")
async def add_items(items: List[Item]):
    """Add items to the Shopping Assistant worksheet"""
    try:
        if not sheets_service:
            raise HTTPException(status_code=500, detail="Google Sheets service not initialized")

        # Create or get the worksheet
        worksheet = sheets_service.create_shopping_worksheet()

        # Get existing items to avoid duplicates
        all_values = worksheet.get_all_values()
        existing_items = [row[0] for row in all_values[1:] if row and len(row) > 0]

        # Add new items
        added_count = 0
        for item in items:
            if item.name not in existing_items:
                # Add the item to the next available row
                next_row = len(all_values) + 1 + added_count  # Increment for each added item
                target_price_str = f"₹{item.target_price:.2f}" if item.target_price else ""

                # Create a row with the item data
                row_data = [[item.name, target_price_str]]
                worksheet.update(f'A{next_row}:B{next_row}', row_data)

                added_count += 1

        return {"status": "success", "message": f"Added {added_count} new items to Shopping Assistant worksheet"}
    except Exception as e:
        logger.error(f"Failed to add items to Shopping Assistant worksheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-indian-prices")
async def update_indian_prices(background_tasks: BackgroundTasks):
    """Manually trigger a price update for Indian retailers"""
    try:
        if not sheets_service or not indian_price_comparator:
            raise HTTPException(status_code=500, detail="Required services not initialized")

        background_tasks.add_task(update_indian_retailer_prices)
        return {"status": "success", "message": "Indian retailer price update started in background"}
    except Exception as e:
        logger.error(f"Failed to start Indian retailer price update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def update_indian_retailer_prices():
    """Update prices from Indian retailers for all items in the Shopping Assistant worksheet"""
    try:
        # Create or get the worksheet
        worksheet = sheets_service.create_shopping_worksheet()

        # Get all items
        all_values = worksheet.get_all_values()

        # Skip header row
        for i, row in enumerate(all_values[1:], start=2):
            if not row or len(row) == 0 or not row[0]:
                continue

            item_name = row[0]
            logger.info(f"Searching for prices for '{item_name}' on Indian retailers")

            # Get prices from all Indian retailers
            results = indian_price_comparator.find_prices(item_name)

            # Update prices for each retailer
            if results["flipkart"]:
                sheets_service.update_retailer_price(
                    worksheet, i, "Flipkart",
                    results["flipkart"]["price"],
                    results["flipkart"]["url"]
                )

            if results["myntra"]:
                sheets_service.update_retailer_price(
                    worksheet, i, "Myntra",
                    results["myntra"]["price"],
                    results["myntra"]["url"]
                )

            if results["ajio"]:
                sheets_service.update_retailer_price(
                    worksheet, i, "Ajio",
                    results["ajio"]["price"],
                    results["ajio"]["url"]
                )

        logger.info("Completed Indian retailer price update")
        return True
    except Exception as e:
        logger.error(f"Failed to update Indian retailer prices: {e}")
        return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
