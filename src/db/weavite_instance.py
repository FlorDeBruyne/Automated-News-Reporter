import os
import weaviate
from weaviate.util import generate_uuid5
import datetime
from dotenv import load_dotenv
load_dotenv()

class WeaviateInstance:
    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL")
        self.client = self._initialize_client()

    def _initialize_client(self):
        return weaviate.connect_to_local(host=str(os.getenv("WEAVIATE_HOST")),
                                         port=int(os.getenv("WEAVIATE_PORT")),
                                         grpc_port=int(os.getenv("WEAVIATE_GRPC")))

    def create_collection(self, schema, schema_name):
        if schema_name not in self.client.collections.list_all():
            self.client.collections.create_from_dict(schema)
            self.client = self.client.collections.get(schema_name)
            print(f"Collection with name {schema_name} created.")
        else:
            self.client = self.client.collections.get(schema_name)
            print(f"Collection with name '{schema_name}' already exists.")


    def create_article(self, title, content, authors, publication_date, category=None, tags=None, url=None, scrape_date=None,  article_id=None):
        if not article_id:
            article_id = generate_uuid5(title + authors)
        created_date = datetime.datetime.now().isoformat()

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

        uuid = self.client.data.insert(
            properties=data_properties,
            uuid=article_id
        )

        print(f"Article with ID '{uuid}' created.")

    def get_article_by_id(self, article_id):
        try:
            article = self.client.query.fetch_object_by_id(
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
                    self.client.data.update(
                        uuid=article_id,
                        class_name="Article",
                        data={key: value}
                    )
                    print(f"Updated {key} for article ID '{article_id}'.")
                else:
                    print(f"Cannot update property '{key}'.")
        except Exception as e:
            print(f"Error updating article: {e}")

    def delete_article_by_id(self, article_id):
        try:
            self.client.data.delete_by_id(
                uuid=article_id
            )
            print(f"Article is deleted")
        except Exception as e:
            print(f"Error deleting article: {e}")
    
    def close_client(self):
        return True if self.client.close() is None else False