import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from uuid import uuid4
import datetime

from dotenv import load_dotenv
load_dotenv()


class ChromadbInstance:
    def __init__(self):
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.client = self._initialize_client()
        

        print("hearbeat: ", self.client.heartbeat())
        


    def _initialize_client(self):
        print("initializing client")
        return chromadb.HttpClient(host=os.getenv("CHROMADB_HOST"),
                                   port=os.getenv("CHROMADB_PORT"))

    #DECREPEATED???
    # def _ollamaEmbedding(self):
    #     print("initializing ollama embedding")
    #     return embedding_functions.OllamaEmbeddingFunction(url=str(os.getenv("OLLAMA_URL")), model_name=str(os.getenv("EMBEDDING_MODEL")))


    def _initialize_collection(self, collection_name):
        print("Initializing collection")
        self.collection_metadata = {"hnsw:space": "cosine", "hnsw:search_ef": 100 }
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata=self.collection_metadata, embedding_function=self.ef)


    def add_document(self, document: dict) -> None:
        try:
            content = document["article_content"]
            metdata = {key: value for key, value in document.items() if key != "article_content"}
            self.collection.add(documents=[content],
                                metadatas=[metdata],
                                ids=[str(self.collection.count()+1)])
        except Exception as e:
            print(f"ERROR while adding document: {str(e)}")
    

    def get_document_by_id(self, document_id: str):
        try:
            return self.collection.get(ids=[document_id])
        except Exception as e:
            print(f"ERROR while getting document by id: {str(e)}")


    def get_document_query(self, query_texts: list, where_metadata: dict, where_documents: dict, top_k: int = 10):
        try:
            return self.collection.query(query_texts=query_texts,
                                         where=where_metadata,
                                         where_document=where_documents,
                                         n_results=top_k)
        except Exception as e:
            print(f"ERROR while getting document by query: {str(e)}")


    def update_document(self, document_id: str, document: dict):
        try:
            content = document["article_content"].value
            metdata = {key: value for key, value in document.items() if key != "article_content"} 
            self.collection.update(ids=[document_id], documents=[content], metadatas=[metdata])
        except Exception as e:
            print(f"ERROR while updating document: {str(e)}")
    

    def delete_document_by_id(self, document_id: str):
        try:
            self.collection.delete(ids=[document_id])
        except Exception as e:
            print(f"ERROR while deleting document: {str(e)}")
    
    
    def delete_document_by_filter(self, filter: dict):
        try:
            self.collection.delete(where=filter)
        except Exception as e:
            print(f"ERROR while deleting document by filter: {str(e)}")
    