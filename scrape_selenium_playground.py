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

logger = getLogger("seleniumplaygroundscrapper.py")
logging.basicConfig(
    stream=sys.stdout,
    format="%(message)s",
    level=logging.DEBUG,
)

# Read LambdaTest username & access key from env file
load_dotenv("sample.env")

capabilities = {
    "browserName": "Chrome",
    "browserVersion": "latest",
    "LT:Options": {
        "platform": "Windows 10",
        "build": "Selenium Playground Scraping",
        "name": "Scrape LambdaTest Selenium Playground",
        "user": os.getenv("LT_USERNAME"),
        "accessKey": os.getenv("LT_ACCESS_KEY"),
        "network": False,
        "video": True,
        "console": True,
        "tunnel": False,  
        "tunnelName": "",  
        "geoLocation": "",
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
        # browser = playwright.chromium.launch() 
        page = browser.new_page()
        try:                        
            page.goto("https://www.lambdatest.com/selenium-playground/")
            # Construct base locator section
            base_container_locator = page.locator("//*[@id='__next']/div/section[2]/div/div/div")
            for item in range(1, base_container_locator.count()+1):                
                # Find section, demo name & demo link with respect to base locator & print them
                locator_row = base_container_locator.locator(f"//div[{item}]")                            
                for inner_item in range(0, locator_row.count()):
                    logger.info(f"*-*-"*28)
                    logger.info(f'Section: {locator_row.nth(inner_item).locator("//h2").all_inner_texts()[0]}\n') 
                    for list_item in range(0,locator_row.nth(inner_item).locator("//ul/li").count()):
                        logger.info(f'Demo Name: {locator_row.nth(inner_item).locator("//ul/li").nth(list_item).all_inner_texts()[0]}')
                        logger.info(f'Demo Link: {locator_row.nth(inner_item).locator("//ul/li/a").nth(list_item).get_attribute("href")}\n')
            status = 'status'
            remark = 'Scraping Completed'
            page.evaluate("_ => {}","lambdatest_action: {\"action\": \"setTestStatus\", \"arguments\": {\"status\":\"" + status + "\", \"remark\": \"" + remark + "\"}}")
        
        except Exception as ex:
            logger.error(str(ex))        
            



if __name__ == "__main__":
    main()
