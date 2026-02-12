import os, sys
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright

topic = "linux"
url = f"https://www.reddit.com/r/{topic}"
contents = []

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    context = browser.new_context()
    
    page = context.new_page()
    page.goto(url, wait_until="load")
    
    while len(contents) < 5000:
        for i in range(25):
            # page.keyboard.down("PageDown")
            page.mouse.wheel(0, 15000)
        
        time.sleep(2)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        batches = soup.find_all("faceplate-batch")
        batch = batches[1] if len(batches) == 2 else batches[0]
        
        articles = batch.find_all("article")
        
        for article in articles:
            title = article["aria-label"]
            content = article.get_text(strip=True)
            contents.append((title, content))
    
    Browser.close()
