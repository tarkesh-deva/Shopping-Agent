import re
from bs4 import BeautifulSoup
from loguru import logger

from agents.base_agent import BaseAgent

class FlipkartAgent(BaseAgent):
    """Agent for checking prices on Flipkart"""

    @property
    def retailer_name(self):
        return "Flipkart"

    def search_product(self, product_name):
        """Search for a product on Flipkart and return its details"""
        try:
            # Format the search URL with men's clothing specific parameters
            search_url = "https://www.flipkart.com/search"

            # Add "men" to the search query if not already present
            search_query = product_name
            if "men" not in product_name.lower():
                search_query = f"men {product_name}"

            params = {
                "q": search_query,
                "otracker": "search",
                "marketplace": "FLIPKART"
            }

            # Add men's clothing specific filters
            men_filter = "p[]=facets.ideal_for%255B%255D%3DMen"
            clothing_filter = "p[]=facets.category%255B%255D%3DClothing"

            # Construct the URL with filters
            search_url = f"{search_url}?{men_filter}&{clothing_filter}"

            # Make the request
            response = self._make_request(search_url, params)
            if not response:
                return None

            # Parse the HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Find the first product result
            product_div = soup.select_one('div._1AtVbE')
            if not product_div:
                logger.warning(f"No product results found for '{product_name}' on Flipkart")
                return None

            # Extract product details
            product_url_element = product_div.select_one('a._1fQZEK, a._2rpwqI, a.s1Q9rs')
            if not product_url_element:
                logger.warning(f"Could not find product URL for '{product_name}' on Flipkart")
                return None

            # Get the product URL
            product_url = "https://www.flipkart.com" + product_url_element['href']

            # Get the product name
            product_name_element = product_div.select_one('div._4rR01T, a.s1Q9rs, div._2WkVRV')
            product_name_text = product_name_element.text.strip() if product_name_element else "Unknown Product"

            # Get the product price
            price_element = product_div.select_one('div._30jeq3')
            if not price_element:
                logger.warning(f"Could not find price for '{product_name}' on Flipkart")
                return None

            # Extract the price value
            price_text = price_element.text.strip()
            # Remove currency symbol (₹) and commas
            price_text = price_text.replace('₹', '').replace(',', '')
            price_match = re.search(r'(\d+)', price_text)
            if not price_match:
                logger.warning(f"Could not parse price '{price_text}' for '{product_name}' on Flipkart")
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
            logger.error(f"Error searching for '{product_name}' on Flipkart: {e}")
            return None
