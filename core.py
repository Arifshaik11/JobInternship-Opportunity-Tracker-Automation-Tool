import os
import json
import logging
import smtplib
import inspect
from email.mime.text import MIMEText
from dotenv import load_dotenv
from importlib import import_module
from pathlib import Path

# --- Import JobScraper base class ---
from scrapers.base_scraper import JobScraper  # <- Added this line

# --- Logging ---
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

# --- Load Environment ---
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SENT_JOBS_FILE = "sent_jobs.json"
KEYWORDS = [kw.strip() for kw in os.getenv("KEYWORDS", "engineer,developer").split(",")]
LOCATIONS = [loc.strip() for loc in os.getenv("LOCATIONS", "india,bangalore,hyderabad").split(",")]

logging.info(f"Keywords: {KEYWORDS}")
logging.info(f"Locations: {LOCATIONS}")

# --- Email Function ---
def send_email(subject: str, body: str) -> None:
    if not EMAIL_USER or not EMAIL_PASS:
        logging.error("EMAIL_USER or EMAIL_PASS not set in .env")
        return
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# --- Sent Jobs Handling ---
def load_sent_jobs(filepath: str) -> set:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_sent_jobs(filepath: str, sent_jobs: set) -> None:
    with open(filepath, "w") as f:
        json.dump(list(sent_jobs), f)

# --- Filter Function ---
def filter_jobs(jobs: list, keywords: list, location_keywords: list, sent_jobs: set) -> list:
    filtered = []
    for job in jobs:
        title = job.get("title", "").lower()
        location = job.get("location", "").lower()
        link = job.get("link")
        if not link or link in sent_jobs:
            continue
        if any(kw.lower() in title for kw in keywords) and any(loc.lower() in location for loc in location_keywords):
            filtered.append(job)
    return filtered

# --- Load Scrapers Dynamically ---
def load_scrapers(folder="scrapers") -> list:
    scrapers = []
    folder_path = Path(folder)
    
    for file in folder_path.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_name = f"{folder}.{file.stem}"
        module = import_module(module_name)
        
        # Find all classes that subclass JobScraper
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, JobScraper) and obj is not JobScraper:
                scrapers.append(obj())
    
    return scrapers

# --- Main ---
def main():
    sent_jobs = load_sent_jobs(SENT_JOBS_FILE)
    scrapers = load_scrapers()
    all_jobs = []
    for scraper in scrapers:
        all_jobs.extend(scraper.scrape())
    logging.info(f"Total jobs scraped: {len(all_jobs)}")
    matches = filter_jobs(all_jobs, KEYWORDS, LOCATIONS, sent_jobs)
    logging.info(f"New matches found: {len(matches)}")
    if matches:
        body = "\n".join([f"{job['title']} ({job['location']}): {job['link']}" for job in matches])
        send_email("Job Matches Alert", body)
        for job in matches:
            sent_jobs.add(job["link"])
        save_sent_jobs(SENT_JOBS_FILE, sent_jobs)

if __name__ == "__main__":
    main()



