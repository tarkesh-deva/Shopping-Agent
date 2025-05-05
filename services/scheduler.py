from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from loguru import logger

import config

class Scheduler:
    """Service for scheduling periodic tasks"""
    
    def __init__(self, sheets_service, price_comparator, whatsapp_service):
        """Initialize the scheduler"""
        self.sheets_service = sheets_service
        self.price_comparator = price_comparator
        self.whatsapp_service = whatsapp_service
        
        # Create scheduler
        self.scheduler = BackgroundScheduler()
        
        # Add job for updating prices
        self.scheduler.add_job(
            self.update_prices,
            IntervalTrigger(minutes=config.UPDATE_INTERVAL_MINUTES),
            id='update_prices',
            name='Update prices and check for drops',
            replace_existing=True
        )
        
        logger.info(f"Scheduler initialized with {config.UPDATE_INTERVAL_MINUTES} minute intervals")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    async def update_prices(self):
        """Update prices for all items and check for price drops"""
        logger.info("Starting scheduled price update")
        
        try:
            # Get all items from the sheet
            items = self.sheets_service.get_all_items()
            
            # Track items with price drops
            price_drops = []
            
            # Process each item
            for item in items:
                try:
                    # Skip items without a name
                    if not item["name"]:
                        continue
                    
                    # Search for the item
                    logger.info(f"Searching for best price for: {item['name']}")
                    result = self.price_comparator.find_best_price(item["name"])
                    
                    if result:
                        # Get the current price from the sheet
                        current_price = item["current_price"]
                        
                        # Check if this is a better price
                        if not current_price or result["price"] < current_price:
                            # Update the sheet
                            self.sheets_service.update_item_price(
                                item["id"],
                                result["price"],
                                result["url"],
                                result["retailer"]
                            )
                            
                            # Check if this is a significant price drop
                            if current_price and item["target_price"]:
                                drop_percent = (current_price - result["price"]) / current_price * 100
                                
                                if drop_percent >= config.PRICE_DROP_THRESHOLD_PERCENT:
                                    # Add to price drops list
                                    price_drops.append({
                                        **item,
                                        "current_price": result["price"],
                                        "url": result["url"],
                                        "retailer": result["retailer"]
                                    })
                except Exception as e:
                    logger.error(f"Error processing item {item['name']}: {e}")
                    continue
            
            # Send notifications for price drops
            for item in price_drops:
                self.whatsapp_service.send_price_drop_alert(item)
            
            logger.info(f"Price update completed. Found {len(price_drops)} price drops.")
            return True
        except Exception as e:
            logger.error(f"Failed to update prices: {e}")
            return False
