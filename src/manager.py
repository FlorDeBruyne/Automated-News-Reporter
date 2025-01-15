from script.fetch_articles import ArticleScraper
from db.chromadb_instance  import ChromadbInstance
import json
import os
import datetime

def main():
    # scraper = ArticleScraper("Technology")
    # # scraper.scrape_article()
    # print(scraper.scrape_article_links())

        # scraper.driver.quit()
    

    try:
        chromadb_instance = ChromadbInstance()

        # # Create an article
        article_id = "001"
        article_title = "Enhanced Sample Article"
        article_content = "This is an enhanced sample article content."
        article_authors = ["John Doe", "Jane Smith"]
        article_publication_date = datetime.datetime.now()
        article_category = "Technology"
        article_tags = ["AI", "Python"]
        article_url = "http://example.com/article-001"


        chromadb_instance.add_document(
            {
                "article_id": article_id,
                "article_title": article_title,
                "article_content": article_content,
                "article_authors": article_authors,
                "article_publication_date": article_publication_date,
                "article_category": article_category,
                "article_tags": article_tags,
                "article_url": article_url,
                "creation_date": datetime.datetime.now()
            }
        )

        # Retrieve an article by ID
        retrieved_article = chromadb_instance.get_document_query_metadata({"article_id": article_id})
        print("Retrieved Article:", retrieved_article)

        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        chromadb_instance.close_client()



if __name__ == "__main__":
    main()