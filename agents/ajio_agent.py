import re
from bs4 import BeautifulSoup
from loguru import logger

from agents.base_agent import BaseAgent

class AjioAgent(BaseAgent):
    """Agent for checking prices on Ajio"""

    @property
    def retailer_name(self):
        return "Ajio"

    def _determine_category(self, product_name):
        """Determine the appropriate Ajio category based on the product name"""
        product_name = product_name.lower()

        # Map common clothing items to Ajio categories
        if any(item in product_name for item in ["t-shirt", "tshirt", "t shirt"]):
            return "830216001"  # Men's T-shirts
        elif any(item in product_name for item in ["shirt", "oxford", "chambray", "button down", "dress shirt"]):
            return "830216003"  # Men's Shirts
        elif any(item in product_name for item in ["jeans", "denim"]):
            return "830216013"  # Men's Jeans
        elif any(item in product_name for item in ["trouser", "chino", "pant"]):
            return "830216005"  # Men's Trousers
        elif any(item in product_name for item in ["jacket", "bomber", "denim jacket"]):
            return "830216002"  # Men's Jackets
        elif "hoodie" in product_name:
            return "830216011"  # Men's Sweatshirts
        elif "polo" in product_name:
            return "830216001"  # Men's T-shirts & Polos
        elif "suit" in product_name:
            return "830216004"  # Men's Suits
        elif "shoe" in product_name or "sneaker" in product_name or "footwear" in product_name:
            return "830216006"  # Men's Casual Shoes
        elif "formal shoe" in product_name:
            return "830216007"  # Men's Formal Shoes
        elif "boot" in product_name:
            return "830216008"  # Men's Boots
        elif "short" in product_name:
            return "830216014"  # Men's Shorts

        # Default to a general category if no specific match
        return "men"  # Men's category

    def search_product(self, product_name):
        """Search for a product on Ajio and return its details"""
        try:
            # Format the search URL with men's clothing specific parameters

            # Add "men" to the search query if not already present
            search_query = product_name
            if "men" not in product_name.lower():
                search_query = f"men {product_name}"

            # Determine the appropriate category based on the product name
            category = self._determine_category(search_query)

            # Ajio uses a different URL structure for categories
            search_url = f"https://www.ajio.com/s/{category}"
            params = {
                "query": search_query,
                "gclid": "men",
                "segment": "Men"
            }

            # Make the request
            response = self._make_request(search_url, params)
            if not response:
                return None

            # Parse the HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Find the first product result
            product_div = soup.select_one('div.item.rilrtl-products-list__item')
            if not product_div:
                logger.warning(f"No product results found for '{product_name}' on Ajio")
                return None

            # Extract product details
            product_url_element = product_div.select_one('a.rilrtl-products-list__link')
            if not product_url_element:
                logger.warning(f"Could not find product URL for '{product_name}' on Ajio")
                return None

            # Get the product URL
            product_url = "https://www.ajio.com" + product_url_element['href']

            # Get the product name
            brand_element = product_div.select_one('div.brand')
            product_element = product_div.select_one('div.nameCls')

            brand_name = brand_element.text.strip() if brand_element else ""
            product_desc = product_element.text.strip() if product_element else "Unknown Product"
            product_name_text = f"{brand_name} {product_desc}".strip()

            # Get the product price
            price_element = product_div.select_one('span.price')
            if not price_element:
                logger.warning(f"Could not find price for '{product_name}' on Ajio")
                return None

            # Extract the price value
            price_text = price_element.text.strip()
            # Remove currency symbol (₹) and commas
            price_text = price_text.replace('Rs.', '').replace('₹', '').replace(',', '')
            price_match = re.search(r'(\d+)', price_text)
            if not price_match:
                logger.warning(f"Could not parse price '{price_text}' for '{product_name}' on Ajio")
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
            logger.error(f"Error searching for '{product_name}' on Ajio: {e}")
            return None
