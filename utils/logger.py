import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get log level from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="1 week",
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Export logger
__all__ = ["logger"]
