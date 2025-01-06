import os, time, json, re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from src.db.mongo_instance import MongoInstance
from dotenv import load_dotenv
load_dotenv()

class ArticleScraper():
    def __init__(self, topic):
        self.topic = topic
        self.driver = webdriver.Chrome(self._get_driver())
        self.mongo = MongoInstance("automated_news_report")
        self.site_configs = {}
        self.article_links = {}


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
        site_configs = self.mongo.find({})
        return site_configs
        
    
    def _get_article_data(self) -> None:
        """
        Extract article data from the site configurations
        """
        try:
            site_configs = self._get_site_configs()
            
            # Process each document in the site_configs
            for config in site_configs:
                if self.topic in config:
                    topic_data = config[self.topic]

                    # Iterate through the categories 
                    for category, sites in topic_data.items():
                        if category not in self.site_configs:
                            self.site_configs[category] = {}

                        # Extract site configurations for each site
                        for site_name, site_data in sites.items():
                            self.site_configs[category][site_name] = site_data
        except Exception as e:
            print(f"An error occurred while getting article data: {e}")
    
    def _extract_article_content(self, soup):
        """
        Scrape article content from the article links and save to weaviate and mongodb databases
        """
        article_content = ""
        article = soup.find_all("article")
        if article:
            article_content = article[0].get_text()
        return article_content
    
    def scrape_article_links(self):
        """
        Collect article links from sources that are in the Mongodb collection
        """
        self._get_article_data()

        for category, sites in self.site_configs.items():
            print(f"Processing category: {category}, description: {sites}")
            for site_name, site_data in sites["sources"].items():
                print(f"Processing site: {site_name}, site_date: {site_data}")
                url = site_data["base_url"]
                self.driver.get(url)
                time.sleep(100)

                if "cookies_button_id" in site_data:
                    print("looking for cookies button")
                    cookies_button = self.driver.find_element(By.ID, site_data["cookies_button_id"])
                    cookies_button.click()
                    time.sleep(10)
                
                if "cookies_button_class" in site_data:
                    print("looking for cookies button")
                    cookies_button = self.driver.find_element(By.CLASS_NAME, site_data["cookies_button_class"])
                    cookies_button.click()
                    time.sleep(10)

                for article_classes in site_data["article_class"]:
                    print(f"Processing article class: {article_classes}")
                    article = self.driver.find_elements(By.CLASS_NAME, article_classes)
                    if article:
                        print(article[0].get_text())
                    else:
                        print("No article found")
    
    def scrape_articles(self):
        """
        Scrape articles from the article links and save to weaviate and mongodb databases
        """
        pass
    
       

