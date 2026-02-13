import os, sys
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright

contents = []

def reddit_scrapper(topic: str):
    global contents
    print(f"contents size: {len(contents)}")
    
    url = f"https://www.reddit.com/r/{topic}"
    
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        
        page = context.new_page()
        page.goto(url, wait_until="load")
        final_line = ""
        
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
            if articles[-1]["aria-label"] == final_line:
                break
            
            final_line = articles[-1]["aria-label"]
            for article in articles:
                title = article["aria-label"].replace('\n', ' ')
                content = article.get_text(strip=True).replace('\n', ' ')
                contents.append(title + ' ' + content)
                
        browser.close()

if __name__ == "__main__":
    topics = ["Ubuntu", "debian", "Kalilinux", "archlinux", "Gentoo",
              "redhat", "Fedora", "openSUSE", "linuxmint", "slackware"]
    
    for topic in topics:
        reddit_scrapper(topic)

    with open("output.txt", 'w') as fp:
        fp.write('\n'.join(contents))
