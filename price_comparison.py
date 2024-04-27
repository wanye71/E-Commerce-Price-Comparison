import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_product_prices(urls, css_selectors=None, max_products=10, timeout=10):
    # Function to scrape the prices of products from the first 10 products on multiple online stores using Selenium.
    #
    # Parameters:
    #   urls (list): A list of URLs of the product pages to scrape.
    #   css_selectors (dict): A dictionary where keys are the URLs and values are the corresponding CSS selectors
    #                         of the element containing the product price. If None, default selectors will be used.
    #   max_products (int): The maximum number of products to scrape prices for on each website.
    #   timeout (int): The maximum time to wait for the element to become visible (in seconds).
    #
    # Returns:
    #   dict: A dictionary where keys are the URLs and values are lists of tuples containing the product name and price,
    #         or an empty dictionary if prices cannot be scraped for any URL.
    
    # Initialize the Chrome browser
    driver = webdriver.Chrome()
    
    prices = {url: [] for url in urls}  # Dictionary to store scraped prices
    
    try:
        for url in urls:
            # Navigate to the URL
            driver.get(url)
            
            # Use custom CSS selector if provided, otherwise use default selector
            css_selector = css_selectors.get(url) if css_selectors else 'span.price-item'
            
            # Wait for the price elements to become visible
            price_elements = WebDriverWait(driver, timeout).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )
            
            # Extract the text of each price element and store it in the dictionary
            for i, price_element in enumerate(price_elements):
                if i >= max_products:
                    break  # Stop scraping if we've collected prices for the maximum number of products
                price = price_element.text.strip()
                prices[url].append(price)
    except Exception as e:
        logging.error(f"Error occurred while scraping prices: {e}")
        return {}
    finally:
        # Close the WebDriver
        driver.quit()
    
    return prices


def compare_prices(prices):
    # Function to compare prices scraped from different websites and identify the best deal for each product.
    #
    # Parameters:
    #   prices (dict): A dictionary where keys are the URLs and values are lists of tuples containing the product name and price.
    #
    # Returns:
    #   dict: A dictionary where keys are the product names and values are tuples containing the best deal URL and price.
    
    # Check if prices dictionary is empty
    if not prices:
        return 'No prices found'
    
    best_deals = {}  # Dictionary to store the best deals for each product
    
    # Iterate through the products and their prices from each website
    for url, product_prices in prices.items():
        for i, product_price in enumerate(product_prices):
            # Parse the product name and price
            product_name = f'Product {i+1}'
            product_price_float = float(product_price.replace('$', '').replace(',', ''))
            
            # Check if product already exists in best_deals dictionary
            if product_name not in best_deals:
                best_deals[product_name] = {'url': url, 'price': product_price_float}
            else:
                # Update best deal if price is lower than current best price
                if product_price_float < best_deals[product_name]['price']:
                    best_deals[product_name] = {'url': url, 'price': product_price_float}
    
    return best_deals


# Configure logging
logging.basicConfig(level=logging.INFO)

# Example usage with custom CSS selectors
urls = [
    'https://hatworld.com.au/collections/leather-hats-1',
    'https://www.outbacktrading.com/collections/leather-hats'
]

css_selectors = {
    'https://hatworld.com.au/collections/leather-hats-1': 'span.price-item',
    'https://www.outbacktrading.com/collections/leather-hats': 'strong.price__current'
}

# Scrape product prices
product_prices = scrape_product_prices(urls, css_selectors)
print('Product Prices:', product_prices)

# Compare prices and identify the best deal for each product
best_deals = compare_prices(product_prices)
print('Best Deals:', best_deals)
