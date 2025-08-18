# scrapers/base_scraper.py
class JobScraper:
    """Base class for all scrapers."""
    def scrape(self):
        """This method should be implemented by all scraper subclasses."""
        raise NotImplementedError("Each scraper must implement the scrape() method")