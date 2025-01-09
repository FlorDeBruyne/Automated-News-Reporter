from script.fetch_articles import ArticleScraper
from db.weavite_instance import WeaviateInstance
import json
import os
import datetime

def main():
    # scraper = ArticleScraper("Technology")
    # # scraper.scrape_article()
    # print(scraper.scrape_article_links())

        # scraper.driver.quit()
        # Initialize the Weaviate instance
    weaviate_instance = WeaviateInstance()
    with open(os.path.join(os.getcwd(), "db/weavit_collection_schema.json")) as f:
        schema = json.load(f)
    # Create the class
    weaviate_instance.create_collection(schema=schema, schema_name="Article")

    # # Create an article
    article_id = "article-001"
    article_title = "Enhanced Sample Article"
    article_content = "This is an enhanced sample article content."
    article_authors = ["John Doe", "Jane Smith"]
    article_publication_date = datetime.datetime.now(datetime.timezone.utc)
    article_category = "Technology"
    article_tags = ["AI", "Weaviate", "Python"]
    article_url = "http://example.com/article-001"


    weaviate_instance.create_article(
        title=article_title,
        content=article_content,
        authors=str(article_authors),
        publication_date=article_publication_date,
        category=article_category,
        tags=article_tags,
        url=article_url,
        scrape_date=datetime.datetime.now(datetime.timezone.utc),
        # article_id=article_id
    )

    # Retrieve an article by ID
    retrieved_article = weaviate_instance.get_article_by_id(article_id, str(article_authors))
    print("Retrieved Article:", retrieved_article)

    # Update an article
    weaviate_instance.update_article(article_id, title="Updated Enhanced Sample Article")

    # Delete an article
    weaviate_instance.delete_collection(collection_name="Article")
    weaviate_instance.close_client()



if __name__ == "__main__":
    main()