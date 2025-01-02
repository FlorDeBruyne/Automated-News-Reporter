import json
from bs4 import BeautifulSoup
import requests

class RuleBasedScraper:
    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.config = json.load(f)

    def scrape(self, site_name):
        rules = self.config[site_name]
        html = requests.get(rules["base_url"]).text
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select(rules["article_selector"])
        return [
            {
                "title": article.select_one(rules["title_selector"]).text.strip(),
                "url": article.select_one(rules["url_selector"])["href"]
            }
            for article in articles
        ]

scraper = RuleBasedScraper("site_configs.json")
articles = scraper.scrape("TechCrunch")
print(articles)