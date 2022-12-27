import json
import logging
import os
import subprocess
import sys
import time
import urllib
from logging import getLogger

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# setup basic loggig for our project which will display the time, log level & log message
logger = getLogger("webscapper.py")
logging.basicConfig(
    stream=sys.stdout,  # uncomment this line to redirect output to console
    format="%(message)s",
    level=logging.DEBUG,
)

# LambdaTest username & access key are stored in an env file & we fetch it from there using python dotenv module
load_dotenv("sample.env")

capabilities = {
    "browserName": "Chrome",  # Browsers allowed: `Chrome`, `MicrosoftEdge`, `pw-chromium`, `pw-firefox` and `pw-webkit`
    "browserVersion": "latest",
    "LT:Options": {
        "platform": "Windows 10",
        "build": "E Commerce Scrape Build",
        "name": "Scrape Lambda Software Product",
        "user": os.getenv("LT_USERNAME"),
        "accessKey": os.getenv("LT_ACCESS_KEY"),
        "network": False,
        "video": True,
        "console": True,
        "tunnel": False,  # Add tunnel configuration if testing locally hosted webpage
        "tunnelName": "",  # Optional
        "geoLocation": "",  # country code can be fetched from https://www.lambdatest.com/capabilities-generator/
    },
}


def main():
    with sync_playwright() as playwright:
        playwright_version = (
            str(subprocess.getoutput("playwright --version")).strip().split(" ")[1]
        )
        capabilities["LT:Options"]["playwrightClientVersion"] = playwright_version
        lt_cdp_url = (
            "wss://cdp.lambdatest.com/playwright?capabilities="
            + urllib.parse.quote(json.dumps(capabilities))
        )
        logger.info(f"Initiating connection to cloud playwright grid")
        browser = playwright.chromium.connect(lt_cdp_url)        
        # comment above line & uncomment below line to test on local grid
        # browser = playwright.chromium.launch(headless=False) 
        page = browser.new_page()
        try:            
            # section to navigate to software category  
            page.goto("https://ecommerce-playground.lambdatest.io/")
            page.get_by_role("button", name="Shop by Category").click()
            page.get_by_role("link", name="Software").click()
            page_to_be_scrapped = page.get_by_role(
                "combobox", name="Show:"
            ).select_option(
                "https://ecommerce-playground.lambdatest.io/index.php?route=product/category&path=17&limit=75"
            )
            page.goto(page_to_be_scrapped[0])
            
            # Since image are lazy-loaded scroll to bottom of page
            # the range is dynamically decided based on the number of items i.e. we take the range from limit
            # https://ecommerce-playground.lambdatest.io/index.php?route=product/category&path=17&limit=75
            for i in range(int(page_to_be_scrapped[0].split("=")[-1])):
                page.mouse.wheel(0, 300)
                i += 1
                time.sleep(0.1)
            # Construct locators to identify name, price & image
            base_product_row_locator = page.locator("#entry_212408").locator(".row").locator(".product-grid")
            product_name = base_product_row_locator.get_by_role("heading")
            product_price = base_product_row_locator.locator(".price-new")
            product_image = (
                base_product_row_locator.locator(".carousel-inner")
                .locator(".active")
                .get_by_role("img")
            )            
            total_products = base_product_row_locator.count()
            for product in range(total_products):
                logger.info(
                    f"\n**** PRODUCT {product+1} ****\n"
                    f"Product Name = {product_name.nth(product).all_inner_texts()[0]}\n"
                    f"Price = {product_price.nth(product).all_inner_texts()[0]}\n"
                    f"Image = {product_image.nth(product).get_attribute('src')}\n"
                )
            status = 'status'
            remark = 'Scraping Completed'
            page.evaluate("_ => {}","lambdatest_action: {\"action\": \"setTestStatus\", \"arguments\": {\"status\":\"" + status + "\", \"remark\": \"" + remark + "\"}}")            
        except Exception as ex:
            logger.error(str(ex))


if __name__ == "__main__":
    main()
