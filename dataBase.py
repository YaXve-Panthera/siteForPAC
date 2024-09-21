from dataclasses import asdict
import pymongo
from bson.objectid import ObjectId


class DataBase:
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")

    def __init__(self, dbName):
        self.dataBase = self.db_client[dbName]
        self.userCollection = self.dataBase["users"]

    def addUser(self, user):
        inserted = self.userCollection.insert_one(user)
        self.userCollection.update_one({'email': user['email']}, {'$set': {'id': str(inserted.inserted_id)}})

    def checkUser(self, email):
        if self.userCollection.find_one({'email': email}) is None:
            return True
        else:
            return False

    def getUser(self, id):
        print(id)
        if id is None:
            return False
        return self.userCollection.find_one({'id': id})

    def getUserByEmail(self, email):
        print("request by email " + str(self.userCollection.find_one({'email': email})))
        return self.userCollection.find_one({'email': email})
