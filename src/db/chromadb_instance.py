import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from uuid import uuid4
import datetime

from dotenv import load_dotenv
load_dotenv()


class ChromadbInstance:
    def __init__(self):
        self.client = self._initialize_client()


    def _initialize_client(self):
        return chromadb.AsyncHttpClient(host=os.getenv("CHROMADB_HOST"),
                                   port=os.getenv("CHROMADB_PORT"))


    def _initialize_collection(self, collection_name, metadata:dict={"hnsw:space": "cosine", "hnsw:search_ef": 100, }):
        self.collection = self.client.get_or_create_collection(collection_name, metadata=metadata, embedding_function=self._ollamaEmbedding())


    def _ollamaEmbedding(self):
        return embedding_functions.OllamaEmbeddingFunction(url=str(os.getenv("OLLAMA_URL")), model_name=str(os.getenv("EMBEDDING_MODEL")))

    
    def add_document(self, document: dict) -> None:
        try:
            content = document["article_content"].value
            metdata = {key: value for key, value in document.items() if key != "article_content"}
            self.collection.add(documents=[content],
                                metadatas=[metdata],
                                ids=[self.collection.count()+1])
        except Exception as e:
            print(f"ERROR: {str(e)}")
    

    def get_document_by_id(self, document_id: str):
        try:
            return self.collection.get(ids=[document_id])
        except Exception as e:
            print(f"ERROR: {str(e)}")


    def get_document_query_metadata(self, query_metadata: dict, top_k: int = 10):
        try:
            return self.collection.query(where=query_metadata, n_results=top_k)
        except Exception as e:
            print(f"ERROR: {str(e)}")


    def get_document_query_document(self, query_document: dict, top_k: int = 10):
        try:
            return self.collection.query(where_document=query_document, n_results=top_k)
        except Exception as e:
            print(f"ERROR: {str(e)}")


    def get_document_query_text(self, query_text: str, top_k: int = 10):
        try:
            return self.collection.query(query_texts=[query_text], n_results=top_k)
        except Exception as e:
            print(f"ERROR: {str(e)}")
        
    def update_document(self, document_id: str, document: dict):
        try:
            content = document["article_content"].value
            metdata = {key: value for key, value in document.items() if key != "article_content"} 
            self.collection.update(ids=[document_id], documents=[content], metadatas=[metdata])
        except Exception as e:
            print(f"ERROR: {str(e)}")
    

    def delete_document_by_id(self, document_id: str):
        try:
            self.collection.delete(ids=[document_id])
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    
    def delete_document_by_filter(self, filter: dict):
        try:
            self.collection.delete(where=filter)
        except Exception as e:
            print(f"ERROR: {str(e)}")


    def close_client(self):
        return True if self.client.close() is None else False
    