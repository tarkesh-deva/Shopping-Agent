import requests
from abc import ABC, abstractmethod
from loguru import logger

import config

class BaseAgent(ABC):
    """Base class for price checking agents"""

    def __init__(self):
        """Initialize the agent"""
        # Use a more modern and mobile user agent to avoid detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    @property
    @abstractmethod
    def retailer_name(self):
        """Return the name of the retailer"""
        pass

    @abstractmethod
    def search_product(self, product_name):
        """
        Search for a product and return its details

        Args:
            product_name (str): The name of the product to search for

        Returns:
            dict: Product details with keys:
                - price (float): The price of the product
                - url (str): The URL to purchase the product
                - retailer (str): The name of the retailer
                - name (str): The exact product name as listed
        """
        pass

    def _make_request(self, url, params=None):
        """Make an HTTP request with error handling and retries"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Add a small delay between retries to avoid rate limiting
                if retry_count > 0:
                    import time
                    time.sleep(2)

                response = requests.get(url, headers=self.headers, params=params, timeout=15)

                # Check for common error status codes
                if response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}. Trying with different headers.")
                    # Try with a different user agent on retry
                    self.headers['User-Agent'] = 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
                    retry_count += 1
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url} (attempt {retry_count+1}/{max_retries}): {e}")
                retry_count += 1

                if retry_count >= max_retries:
                    logger.error(f"Max retries reached for {url}")
                    return None
