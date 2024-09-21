from dataclasses import asdict
from user import User
import pymongo


class DataBase:
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")

    def __init__(self, dbName):
        self.dataBase = self.db_client[dbName]
        self.userCollection = self.dataBase["users"]

    def addUser(self, user):
        self.userCollection.insert_one(asdict(user))

    def checkUser(self, email):
        if self.userCollection.find_one({'email': email}) is None:
            return True
        else:
            return False