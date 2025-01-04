import os
from ssh_pymongo import MongoSession

from dotenv import load_dotenv, dotenv_values
load_dotenv()

class MongoInstance(MongoSession):

     def __init__(self, databaseName:str) -> None:
          self.client = MongoSession(
               host=str(os.getenv("REMOTE_SERVER")),
               port=22,
               user=str(os.getenv("SSH_USER")),
               password=str(os.getenv("SSH_AUTHENTICATION")),
               uri=str(os.getenv("MONGOSTRING")))
          
          self.database = self.client.connection[databaseName]

     def __repr__(self) -> str:
               return("Databases available:", self.client.list_database_names())

     def select_collection(self, name:str):
          if self.database[name] == None:
               self.database.create_collection(name)
               self.collection = self.database[name]
          else:
               self.collection = self.database[name]
          
     def insert_data(self, data):
          self.collection.insert_one(data)

     def update_data(self, query, new_values):
          self.collection.update_many(query, new_values)

     def delete_data(self, query):
          self.collection.delete_many(query)

     def retrieve_data(self, query):
          return self.collection.find(query)

     def aggregate(self, query):
          return self.collection.aggregate(query)

     def close(self):
          self.client.close()

     def find(self, query):
          return self.collection.find(query)

     def count_documents(self, query):
          return self.collection.count_documents(query)
    
            
            

