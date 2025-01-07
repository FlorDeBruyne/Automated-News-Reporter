import os, time, json, sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as soup
from db.mongo_instance import MongoInstance
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
        return chrome_options
    

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
            self.mongo.select_collection("raw_news_data")
            self.mongo.insert_one(article_content)

            # Save to Weaviate
            # self.weaviate.insert_one(article_content)


        except Exception as e:
            print(f"An error occurred while extracting article content: {e}")
    

    def scrape_article_links(self):
        """
        Collect article links from sources that are in the Mongodb collection
        Get the all the article urls, titles (, authors) with the article_classes 
        """
        self._get_article_data()

        for category, sites in self.site_configs.items():
            print(f"Processing category: {category}, description: {sites["description"]}")
            for site_name, site_data in sites["sources"].items():
                print(f"Processing site: {site_name}, site_date: {site_data}")
                url = site_data["base_url"]
                self.driver.get(url)
                time.sleep(10)

                if "cookies_button_id" in site_data:
                    print("looking for cookies button")
                    cookies_button = self.driver.find_element(By.ID, site_data["cookies_button_id"])
                    cookies_button.click()
                    print("clicked cookies button")
                    time.sleep(10)
                
                if "cookies_button_class" in site_data:
                    try:
                        print("looking for cookies button")
                        cookies_button = self.driver.find_element(By.CLASS_NAME, site_data["cookies_button_class"])
                        cookies_button.click()
                        print("clicked cookies button")
                        time.sleep(6000)
                    except Exception as e:
                        print(f"An error occurred while clicking cookies button: {e}")

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
                                # print(article)
                        else:
                            print(f"No articles found: {article_key}, {article_cont}")
                else:
                    continue
        

    def scrape_articles(self):
        """
        Scrape articles from the article links and save to weaviate and mongodb databases
        """
        pass
    
       

