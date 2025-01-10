import os
import weaviate
from weaviate.util import generate_uuid5
import weaviate.classes as wvc #To see what datatypes there are.
import datetime
from dotenv import load_dotenv
load_dotenv()


class WeaviateInstance:
    def __init__(self, collection_name: str = "Article"):
        self.client = self._initialize_client()

        
        # if not self.collection:
        #     self._initialize_collection(collection_name=collection_name)

    def _initialize_client(self):
        return weaviate.connect_to_local(host=str(os.getenv("WEAVIATE_HOST")),
                                         port=int(os.getenv("WEAVIATE_PORT")),
                                         grpc_port=int(os.getenv("WEAVIATE_GRPC")))

    def _initialize_collection(self, collection_name):
        if collection_name not in self.client.collections.list_all():
            print(f"There is no collection with name '{collection_name}', You have to create one.")
        else:
            self.collection = self.client.collections.get(collection_name)
            print(f"Collection with name '{collection_name}' is selected.")

    def create_collection(self, schema, schema_name):
        if schema_name not in self.client.collections.list_all():
            self.client.collections.create_from_dict(schema)
            self.collection = self.client.collections.get(schema_name)
            print(f"Collection with name {schema_name} created.")
        else:
            self.collection = self.client.collections.get(schema_name)
            print(f"Collection with name '{schema_name}' already exists.")


    def create_article(self, title, content, authors, publication_date, category=None, tags=None, url=None, scrape_date=None,  article_id=None):
        if not article_id:
            article_id = generate_uuid5(title + authors)
        created_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # ADD PUBLICATION COLLECTION AND MAKE A CONNECTION?
        data_properties = {
            "title": title,
            "content": content,
            "authors": authors,
            "publicationDate": publication_date.isoformat(),
            "category": category,
            "tags": tags,
            "url": url,
            "scrapeDate": scrape_date,
            "createdDate": created_date,
            "articleId": article_id
        }

        uuid = self.collection.data.insert(
            properties=data_properties,
            uuid=article_id
        )

        print(f"Article with ID '{uuid}' created.")

    def get_article_by_id(self, title, authors):
        article_id = generate_uuid5(title + authors)

        try:
            article = self.collection.query.fetch_object_by_id(
                uuid=article_id
            )
            return article
        except Exception as e:
            print(f"Error retrieving article: {e}")
            return None

    def update_article(self, article_id, **kwargs):
        try:
            for key, value in kwargs.items():
                if key in ["title", "content", "authors", "publicationDate", "category", "tags", "url", "views", "likes", "createdDate", "lastModifiedDate"]:
                    self.collection.data.update(
                        uuid=article_id,
                        properties={key: value}
                    )
                    print(f"Updated {key} for article ID '{article_id}'.")
                else:
                    print(f"Cannot update property '{key}'.")
        except Exception as e:
            print(f"Error updating article: {e}")
    
    def delete_collection(self, collection_name):
        try:
            self.client.collections.delete(collection_name)
            print(f"Collection with name {collection_name} is deleted")
        except Exception as e:
            print(f"Error deleting collection: {e}")

    def delete_article_by_id(self, article_id):
        try:
            self.collection.data.delete_by_id(
                uuid=article_id
            )
            print(f"Article is deleted")
        except Exception as e:
            print(f"Error deleting article: {e}")
    
    def close_client(self):
        return True if self.client.close() is None else False
    
    def list_all_articles(self):
        try:
            articles = self.collection.query.get(class_name="Article").do()
            return articles
        except Exception as e:
            print(f"Error listing articles: {e}")
            return []

    def search_articles(self, query):
        try:
            articles = self.collection.query.get(class_name="Article").with_where({
                "path": ["content"],
                "operator": "Like",
                "valueString": f"%{query}%"
            }).do()
            return articles
        except Exception as e:
            print(f"Error searching articles: {e}")
            return []