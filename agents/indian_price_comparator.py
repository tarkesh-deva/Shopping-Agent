from loguru import logger

from agents.flipkart_agent import FlipkartAgent
from agents.myntra_agent import MyntraAgent
from agents.ajio_agent import AjioAgent

class IndianPriceComparator:
    """Compares prices from Indian retailers and finds the best deal"""
    
    def __init__(self):
        """Initialize the price comparator with Indian retail agents"""
        self.agents = [
            FlipkartAgent(),
            MyntraAgent(),
            AjioAgent()
        ]
        
        logger.info(f"Indian Price comparator initialized with {len(self.agents)} agents")
    
    def find_prices(self, product_name):
        """
        Find prices for a product across all Indian retailers
        
        Args:
            product_name (str): The name of the product to search for
            
        Returns:
            dict: Product deals from each retailer with keys:
                - flipkart: dict with price, url, name (or None if not found)
                - myntra: dict with price, url, name (or None if not found)
                - ajio: dict with price, url, name (or None if not found)
                - best_deal: dict with the best deal info
        """
        try:
            logger.info(f"Searching for prices for '{product_name}' on Indian retailers")
            
            # Track results from each retailer
            results = {
                "flipkart": None,
                "myntra": None,
                "ajio": None,
                "best_deal": None
            }
            
            # Check each agent
            for agent in self.agents:
                try:
                    retailer_name = agent.retailer_name.lower()
                    logger.info(f"Checking {agent.retailer_name} for '{product_name}'")
                    result = agent.search_product(product_name)
                    
                    if result:
                        logger.info(f"Found {result['name']} for ₹{result['price']} at {result['retailer']}")
                        results[retailer_name] = result
                        
                        # Update best deal if this is better
                        if (results["best_deal"] is None or 
                            result["price"] < results["best_deal"]["price"]):
                            results["best_deal"] = result
                except Exception as e:
                    logger.error(f"Error with {agent.retailer_name} agent: {e}")
                    continue
            
            if results["best_deal"]:
                logger.info(f"Best deal for '{product_name}': ₹{results['best_deal']['price']} at {results['best_deal']['retailer']}")
            else:
                logger.warning(f"No deals found for '{product_name}' on Indian retailers")
            
            return results
        except Exception as e:
            logger.error(f"Error finding prices for '{product_name}' on Indian retailers: {e}")
            return {
                "flipkart": None,
                "myntra": None,
                "ajio": None,
                "best_deal": None
            }
