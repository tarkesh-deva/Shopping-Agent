from loguru import logger

from agents.amazon_agent import AmazonAgent
from agents.walmart_agent import WalmartAgent
from agents.flipkart_agent import FlipkartAgent
from agents.myntra_agent import MyntraAgent
from agents.ajio_agent import AjioAgent

class PriceComparator:
    """Compares prices from different retailers and finds the best deal"""

    def __init__(self):
        """Initialize the price comparator with agents"""
        self.agents = [
            AmazonAgent(),
            WalmartAgent(),
            FlipkartAgent(),
            MyntraAgent(),
            AjioAgent()
        ]

        logger.info(f"Price comparator initialized with {len(self.agents)} agents")

    def find_best_price(self, product_name):
        """
        Find the best price for a product across all retailers

        Args:
            product_name (str): The name of the product to search for

        Returns:
            dict: Best product deal with keys:
                - price (float): The price of the product
                - url (str): The URL to purchase the product
                - retailer (str): The name of the retailer
                - name (str): The exact product name as listed
        """
        try:
            logger.info(f"Searching for best price for '{product_name}'")

            # Track the best deal
            best_deal = None

            # Check each agent
            for agent in self.agents:
                try:
                    logger.info(f"Checking {agent.retailer_name} for '{product_name}'")
                    result = agent.search_product(product_name)

                    if result:
                        logger.info(f"Found {result['name']} for ${result['price']} at {result['retailer']}")

                        # Update best deal if this is better
                        if not best_deal or result["price"] < best_deal["price"]:
                            best_deal = result
                except Exception as e:
                    logger.error(f"Error with {agent.retailer_name} agent: {e}")
                    continue

            if best_deal:
                logger.info(f"Best deal for '{product_name}': ${best_deal['price']} at {best_deal['retailer']}")
            else:
                logger.warning(f"No deals found for '{product_name}'")

            return best_deal
        except Exception as e:
            logger.error(f"Error finding best price for '{product_name}': {e}")
            return None
