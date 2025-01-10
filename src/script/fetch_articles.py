import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup as soup
from db.mongo_instance import MongoInstance
from db.weavite_instance import WeaviateInstance
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ArticleData:
    title: str
    content: str
    author: str
    publication_date: str
    url: str
    category: str
    tags: List[str]
    source: str
    image_url: Optional[str] = None

class ArticleScraper():
    def __init__(self, topic):
        self.topic = topic
        self.driver = self._initialize_driver()
        self.mongo = MongoInstance("automated_news_report")
        self.weaviate = WeaviateInstance()
        self.site_configs = {}
        self.logger = self._setup_logger()


    def _setup_logger(self) -> logging.Logger:
        """Initialize logger with proper configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler
        fh = logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d")}.log')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger


    def _initialize_driver(self) -> webdriver.Chrome:
        """Initialize Chrome Webdriver with optimized settings"""
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
        return webdriver.Chrome(options=chrome_options)
    

    def _get_site_configs(self):
        self.mongo.select_collection("site_config")
        site_configs = self.mongo.find({})
        return site_configs
    

    def _save_to_weavaite(self, article: ArticleData) -> None:
        """Save article data to Weaviate with proper object structure"""

        weaviate_object = {
            "title": article.title,
            "content": article.content,
            "authors": [article.author] if article.author else ["Unknown"],
            "publicationDate": article.publication_date,
            "category": article.category,
            "tags": [self.topic, article.tags],
            "url": article.url,
            "source": article.source,
            "imageUrl": article.image_url,
            "scrapeDate": datetime.now().isoformat(),
            "createdDate": datetime.now().isoformat()
        }

        try:
            self.weaviate.add_article(weaviate_object)
            self.logger.info(f"Article saved to Weaviate: {article.title}")
        except Exception as e:
            self.logger.error(f"An error occurred while saving article to Weaviate: {str(e)}")
    

    def _handle_cookies(self, site_data):
        """Handle cookie consent popups with better error handling and waiting"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            if "cookies_button_id" in site_data:
                element = wait.until(
                    EC.element_to_be_clickable((By.ID, site_data["cookies_button_id"]))
                )
                element.click()
                
            elif "cookies_button_class" in site_data:
                element = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, site_data["cookies_button_class"]))
                )
                element.click()
                
        except TimeoutException:
            self.logger.warning(f"Cookie button not found or not clickable for {site_data.get('base_url')}")
        except Exception as e:
            self.logger.error(f"Error handling cookies popup: {str(e)}")


    # def _create_weaviate_object(self, article_data, category, source_url):
    #     """
    #     Transform article data into Weaviate object format
    #     """
    #     return {
    #         "title": article_data.get("title", "No title"),
    #         "content": article_data.get("body", "No content"),
    #         "authors": [article_data.get("author", "Unknown")],
    #         "publicationDate": article_data.get("publication_date", datetime.now().isoformat()),
    #         "category": category,
    #         "tags": [self.topic, category],
    #         "url": source_url,
    #         "scrapeDate": datetime.now().isoformat(),
    #         "createdDate": datetime.now().isoformat()
    #     }
        
    
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

    
    def _extract_article_content(self, site_url):
        """
        Scrape article content from the article links and save to weaviate and mongodb databases
        """
        article_content = {}
        try:
            # Extract title
            title_tag = soup.find("h1")
            article_content["title"] = title_tag.get_text(strip=True) if title_tag else "No title found"

            # Extract author
            author_tag = soup.find("span", class_="author")
            article_content["author"] = author_tag.get_text(strip=True) if author_tag else "No author found"

            # Extract publication date
            date_tag = soup.find("time")
            article_content["publication_date"] = date_tag.get_text(strip=True) if date_tag else "No date found"

            # Extract article body
            body_tag = soup.find("div", class_="article-body")
            article_content["body"] = body_tag.get_text(strip=True) if body_tag else "No body found"

            # Save to MongoDB
            # self.mongo.select_collection("raw_news_data")
            # self.mongo.insert_one(article_content)

            return article_content if article_content != "No body found" else None


        except Exception as e:
            print(f"An error occurred while extracting article content: {e}")
    

    def scrape_articles(self) -> None:
        """
        Main scraping method to extract articles from the configured sites 
        """
        self._get_article_data()

        for category, sites in self.site_configs.items():
            print(f"Processing category: {category}, description: {sites["description"]}")
            for site_name, site_data in sites["sources"].items():
                print(f"Processing site: {site_name}, site_date: {site_data}")
                url = site_data["base_url"]
                self.driver.get(url)
                time.sleep(10)

                self._handle_cookies(site_data)

                if "article_class" in site_data:
                    for article_key, article_cont in site_data["article_class"].items():
                        print(f"Processing {article_key}")
                        articles = self.driver.find_elements(By.CLASS_NAME, article_cont)
                        if articles:
                            for article in articles:
                                print(f"Article: {article_key}, {article_cont}")
                                # print(article.text)
                                if article.tag_name == "a" or article.tag_name == "link":
                                    print(article.get_attribute("href"))

                        else:
                            print(f"No articles found: {article_key}, {article_cont}")
                else:
                    continue

        
        self.driver.quit()
       

