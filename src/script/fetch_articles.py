import os, time, json, re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from db.mongo_instance import MongoInstance
from dotenv import load_dotenv
load_dotenv()

class ArticleScraper:
    def __init__(self, site_name, url, output_dir="site_html"):
        self.site_name = site_name
        self.url = url
        self.output_dir = output_dir
        self.driver = self._get_driver()
        self.mongo = MongoInstance("automated_news_reporter")
        self.site_configs = {}


    def _get_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-device-discovery-notifications")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-features=Translate")
    
    def _get_site_configs(self):
        self.mongo.select_collection("site_config")
        site_configs = self.mongo.find()
        yield site_configs
        self.mongo.close()
        
    
    def _get_article_data(self, topic: str) -> None:
        try:
            site_configs = self._get_site_configs()

            # Process each document in the site_configs
            for config in site_configs:
                if topic in config:
                    topic_data = config[topic]

                    # Iterate through the categories (General Tech News, Big Tech-Specific, companies)
                    for category, sites in topic_data.items():
                        if category not in self.site_configs:
                            self.site_configs[category] = {}

                        # Extract site configurations for each site
                        for site_name, site_data in sites.items():
                            self.site_configs[category][site_name] = site_data
        except Exception as e:
            print(f"An error occurred while getting article data: {e}")

    
       

