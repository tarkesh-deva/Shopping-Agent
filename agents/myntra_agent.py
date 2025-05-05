import re
import json
from bs4 import BeautifulSoup
from loguru import logger

from agents.base_agent import BaseAgent

class MyntraAgent(BaseAgent):
    """Agent for checking prices on Myntra"""

    @property
    def retailer_name(self):
        return "Myntra"

    def _determine_category(self, product_name):
        """Determine the appropriate Myntra category based on the product name"""
        product_name = product_name.lower()

        # Map common clothing items to Myntra categories
        if any(item in product_name for item in ["t-shirt", "tshirt", "t shirt"]):
            return "tshirts"
        elif any(item in product_name for item in ["shirt", "oxford", "chambray", "button down", "dress shirt"]):
            return "shirts"
        elif any(item in product_name for item in ["jeans", "denim"]):
            return "jeans"
        elif any(item in product_name for item in ["trouser", "chino", "pant"]):
            return "trousers"
        elif any(item in product_name for item in ["jacket", "bomber", "denim jacket"]):
            return "jackets"
        elif "hoodie" in product_name:
            return "sweatshirts"
        elif "polo" in product_name:
            return "polos"
        elif "suit" in product_name:
            return "suits"
        elif "shoe" in product_name or "sneaker" in product_name or "footwear" in product_name:
            return "casual-shoes"
        elif "formal shoe" in product_name:
            return "formal-shoes"
        elif "boot" in product_name:
            return "boots"
        elif "short" in product_name:
            return "shorts"
        elif "swim" in product_name or "trunk" in product_name:
            return "swimwear"
        elif "belt" in product_name:
            return "belts"
        elif "sunglass" in product_name:
            return "sunglasses"
        elif "watch" in product_name:
            return "watches"
        elif "bag" in product_name:
            return "bags"
        elif "coat" in product_name or "overcoat" in product_name:
            return "coats"

        # Default to a general category if no specific match
        return "clothing"

    def search_product(self, product_name):
        """Search for a product on Myntra and return its details"""
        try:
            # Format the search URL with men's clothing specific parameters

            # Add "men" to the search query if not already present
            search_query = product_name
            if "men" not in product_name.lower():
                search_query = f"men {product_name}"

            # Myntra uses URL path for filtering rather than query parameters
            # Format: https://www.myntra.com/men-tshirts or https://www.myntra.com/men-shirts

            # Determine the appropriate category based on the product name
            category = self._determine_category(search_query)

            # Construct the search URL with category
            search_url = f"https://www.myntra.com/men-{category}"

            params = {
                "q": search_query
            }

            # Make the request
            response = self._make_request(search_url, params)
            if not response:
                return None

            # Parse the HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Find the first product result
            product_div = soup.select_one('li.product-base')
            if not product_div:
                logger.warning(f"No product results found for '{product_name}' on Myntra")
                return None

            # Extract product details
            product_url_element = product_div.select_one('a.product-link')
            if not product_url_element:
                logger.warning(f"Could not find product URL for '{product_name}' on Myntra")
                return None

            # Get the product URL
            product_url = "https://www.myntra.com" + product_url_element['href']

            # Get the product name
            brand_element = product_div.select_one('h3.product-brand')
            product_element = product_div.select_one('h4.product-product')

            brand_name = brand_element.text.strip() if brand_element else ""
            product_desc = product_element.text.strip() if product_element else "Unknown Product"
            product_name_text = f"{brand_name} {product_desc}".strip()

            # Get the product price
            price_element = product_div.select_one('div.product-price > span.product-discountedPrice')
            if not price_element:
                price_element = product_div.select_one('div.product-price > span')

            if not price_element:
                logger.warning(f"Could not find price for '{product_name}' on Myntra")
                return None

            # Extract the price value
            price_text = price_element.text.strip()
            # Remove currency symbol (₹) and commas
            price_text = price_text.replace('Rs.', '').replace('₹', '').replace(',', '')
            price_match = re.search(r'(\d+)', price_text)
            if not price_match:
                logger.warning(f"Could not parse price '{price_text}' for '{product_name}' on Myntra")
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
            logger.error(f"Error searching for '{product_name}' on Myntra: {e}")
            return None
