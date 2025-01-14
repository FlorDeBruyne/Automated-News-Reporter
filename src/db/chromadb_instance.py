import os
import chromadb
from uuid import uuid4
import datetime
from dotenv import load_dotenv
load_dotenv()


class ChromadbInstance:
    def __init__(self, collection_name: str = "Article"):
        self.client = self._initialize_client()


    def _initialize_client(self):
        return chromadb.HttpClient(host=os.getenv("CHROMADB_HOST"),
                                   port=os.getenv("CHROMADB_PORT"))


    def _initialize_collection(self, collection_name, metadata:dict=None):
        self.collection = self.client.get_or_create_collection(collection_name, metadata=metadata)



    # def create_article(self, title, content, authors, publication_date, category=None, tags=None, url=None, scrape_date=None):
    #     try:
    #         if not article_id:
    #             article_id = uuid4()
    #         created_date = datetime.datetime.now().isoformat()

    #         data_properties = {
    #             "title": title,
    #             "content": content,
    #             "authors": authors,
    #             "publicationDate": publication_date.isoformat(),
    #             "category": category,
    #             "tags": tags,
    #             "url": url,
    #             "scrapeDate": scrape_date,
    #             "createdDate": created_date,
    #             "articleId": article_id
    #         }

    #         uuid = self.collection.data.insert(
    #             properties=data_properties,
    #             uuid=article_id
    #         )
    #         print(f"Article with ID '{uuid}' created.")
    #     except Exception as e:
    #         print(f"Didn't create a new articel because of error: {str(e)}")



    

    def close_client(self):
        return True if self.client.close() is None else False