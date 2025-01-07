from script.fetch_articles import ArticleScraper

def main():
    scraper = ArticleScraper("Technology")
    # scraper.scrape_article()
    print(scraper.scrape_article_links())

    # scraper.driver.quit()

if __name__ == "__main__":
    main()