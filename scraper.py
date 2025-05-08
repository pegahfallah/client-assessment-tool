from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

def extract_clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def scrape_airline_pages(base_url, keywords, max_links=20, depth=1):
    visited = set()
    documents = []
    scraped_labels = set()

    def visit(page, url, current_depth):
        if current_depth > depth or url in visited or not url.startswith(base_url):
            return
        visited.add(url)

        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(2000)
            html = page.content()
            clean_text = extract_clean_text(html)
            documents.append({
                "text": clean_text,
                "url": url
            })
        except Exception:
            return

        anchors = page.query_selector_all("a")
        for anchor in anchors:
            try:
                href = anchor.get_attribute("href")
                text = anchor.inner_text() or ""
                if href and any(k in href.lower() or k in text.lower() for k in keywords):
                    full_url = urljoin(base_url, href)
                    scraped_labels.add(text.strip().lower())
                    visit(page, full_url, current_depth + 1)
                    if len(documents) >= max_links:
                        break
            except:
                continue

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        visit(page, base_url, 0)
        browser.close()

    return documents, scraped_labels
