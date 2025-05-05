from twilio.rest import Client
from loguru import logger

import config

class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio"""
    
    def __init__(self):
        """Initialize the WhatsApp service"""
        try:
            # Check if Twilio credentials are configured
            if not all([
                config.TWILIO_ACCOUNT_SID,
                config.TWILIO_AUTH_TOKEN,
                config.TWILIO_WHATSAPP_FROM,
                config.TWILIO_WHATSAPP_TO
            ]):
                logger.warning("Twilio credentials not fully configured. WhatsApp notifications will be disabled.")
                self.enabled = False
                return
            
            # Initialize Twilio client
            self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            self.from_number = f"whatsapp:{config.TWILIO_WHATSAPP_FROM}"
            self.to_number = f"whatsapp:{config.TWILIO_WHATSAPP_TO}"
            self.enabled = True
            
            logger.info("WhatsApp service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp service: {e}")
            self.enabled = False
    
    def send_message(self, message):
        """Send a WhatsApp message"""
        if not self.enabled:
            logger.warning("WhatsApp service is disabled. Message not sent.")
            return False
        
        try:
            # Send the message
            message = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=self.to_number
            )
            
            logger.info(f"WhatsApp message sent successfully. SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return False
    
    def send_price_drop_alert(self, item):
        """Send a price drop alert for a specific item"""
        if not self.enabled:
            logger.warning("WhatsApp service is disabled. Price drop alert not sent.")
            return False
        
        try:
            # Format the message
            message = (
                f"🔔 *Price Drop Alert!*\n\n"
                f"*{item['name']}*\n"
                f"Now only ${item['current_price']:.2f} at {item['retailer']}\n"
                f"(Target price: ${item['target_price']:.2f})\n\n"
                f"Shop now: {item['url']}"
            )
            
            # Send the message
            return self.send_message(message)
        except Exception as e:
            logger.error(f"Failed to send price drop alert: {e}")
            return False
