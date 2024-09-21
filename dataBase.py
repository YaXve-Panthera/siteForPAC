import pymongo


class DataBase:
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")

    def __init__(self, dbName):
        self.dataBase = self.db_client[dbName]
        self.userCollection = self.dataBase["users"]

    def addUser(self, user):
        inserted = self.userCollection.insert_one(user)
        self.userCollection.update_one({'email': user['email']}, {'$set': {'id': str(inserted.inserted_id),
                        'age': "", 'aboutUser': "", 'photo': ""}})

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

    def updateUser(self, id, name, age, aboutUser):
        self.userCollection.update_one({'id': str(id)}, {'$set': {'name': name, 'age': age, 'aboutUser': aboutUser}})
        print(id)
        print(self.userCollection.find_one({'id': str(id)}))
        print("profile updated in bd")

    def getHash(self, id):
        return self.userCollection.find_one({'id': id})['password']

    def updatePassword(self, id, newpassword):
        self.userCollection.update_one({'id': str(id)}, {'$set': {'password': newpassword}})
        print("password is updated")
