import logging
import urllib.parse
import os
from playwright.sync_api import sync_playwright
from scrapers.base_scraper import JobScraper

class GoogleScraper(JobScraper):
    BASE_URL = "https://careers.google.com/jobs/results/"
    MAX_JOBS = 100

    def __init__(self):
        self.keywords = [kw.strip() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]
        self.locations = [loc.strip() for loc in os.getenv("LOCATIONS", "").split(",") if loc.strip()]

    def build_url(self, location=None, page=1):
        params = []
        if self.keywords:
            query = urllib.parse.quote(" ".join(self.keywords))
            params.append(f"q={query}")
        if location:
            params.append(f"location={urllib.parse.quote(location)}")
        params.append(f"page={page}")
        return f"{self.BASE_URL}?{'&'.join(params)}"

    def scrape(self) -> list:
        jobs = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                target_locations = self.locations if self.locations else [None]

                for location in target_locations:
                    current_page = 1
                    while len(jobs) < self.MAX_JOBS:
                        url = self.build_url(location, page=current_page)
                        logging.info(f"Google: Visiting page {current_page} → {url}")
                        page.goto(url, timeout=60000)
                        page.wait_for_load_state("networkidle")

                        job_cards = page.locator("div.sMn82b")
                        count = job_cards.count()
                        logging.info(f"Google: Page {current_page}: Found {count} jobs")

                        if count == 0:
                            break

                        for i in range(count):
                            if len(jobs) >= self.MAX_JOBS:
                                logging.info("Reached job limit of 100. Stopping scraper.")
                                break
                            try:
                                card = job_cards.nth(i)
                                title = card.locator("h3").first.inner_text(timeout=3000).strip()
                                link_elem = card.locator("a").first
                                link = link_elem.get_attribute("href")
                                if link and not link.startswith("http"):
                                    link = "https://careers.google.com/" + link.lstrip("/")
                                loc_elem = card.locator("span.r0wTof").all_text_contents()
                                location_text = ", ".join([l.strip() for l in loc_elem])

                                # Location is mandatory, keywords optional
                                if location_text and (not self.keywords or any(k.lower() in title.lower() for k in self.keywords)):
                                    jobs.append({"title": title, "link": link, "location": location_text})
                            except Exception as e:
                                logging.warning(f"Failed to parse card {i} on page {current_page}: {e}")

                        next_page_link = page.locator("a[aria-label*='Go to next page']")
                        if next_page_link.count() == 0 or len(jobs) >= self.MAX_JOBS:
                            break
                        current_page += 1

                browser.close()

        except Exception as e:
            logging.error(f"Google: Scraping error: {e}")

        logging.info(f"Google: Total jobs found: {len(jobs)}")
        return jobs
