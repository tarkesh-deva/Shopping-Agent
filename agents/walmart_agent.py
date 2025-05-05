import re
from bs4 import BeautifulSoup
from loguru import logger

from agents.base_agent import BaseAgent

class WalmartAgent(BaseAgent):
    """Agent for checking prices on Walmart"""
    
    @property
    def retailer_name(self):
        return "Walmart"
    
    def search_product(self, product_name):
        """Search for a product on Walmart and return its details"""
        try:
            # Format the search URL
            search_url = "https://www.walmart.com/search"
            params = {
                "q": product_name
            }
            
            # Make the request
            response = self._make_request(search_url, params)
            if not response:
                return None
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find the first product result
            product_div = soup.select_one('div[data-item-id]')
            if not product_div:
                logger.warning(f"No product results found for '{product_name}' on Walmart")
                return None
            
            # Extract product details
            product_url_element = product_div.select_one('a[link-identifier="linkText"]')
            if not product_url_element:
                logger.warning(f"Could not find product URL for '{product_name}' on Walmart")
                return None
            
            # Get the product URL
            product_url = "https://www.walmart.com" + product_url_element['href']
            
            # Get the product name
            product_name_element = product_url_element.select_one('span.lh-title')
            product_name_text = product_name_element.text.strip() if product_name_element else "Unknown Product"
            
            # Get the product price
            price_element = product_div.select_one('div[data-automation-id="product-price"] span.w_iUH7')
            if not price_element:
                logger.warning(f"Could not find price for '{product_name}' on Walmart")
                return None
            
            # Extract the price value
            price_text = price_element.text.strip()
            price_match = re.search(r'(\d+\.\d+)', price_text)
            if not price_match:
                logger.warning(f"Could not parse price '{price_text}' for '{product_name}' on Walmart")
                return None
            
            price = float(price_match.group(1))
            
            # Return the product details
            return {
                "price": price,
                "url": product_url,
                "retailer": self.retailer_name,
                "name": product_name_text
            }
        except Exception as e:
            logger.error(f"Error searching for '{product_name}' on Walmart: {e}")
            return None
