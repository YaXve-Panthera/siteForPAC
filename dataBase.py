import pymongo
from bson import ObjectId


class DataBase:
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")

    def __init__(self, dbName):
        self.dataBase = self.db_client[dbName]
        self.userCollection = self.dataBase["users"]
        self.chatCollection = self.dataBase["chats"]
        self.messagesCollection = self.dataBase["messages"]

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

    def listOfUsers(self):
        l = []
        for user in self.userCollection.find():
            l.append((user['id'], user['name']))
        return l

    def getNameById(self, id):
        return self.userCollection.find_one({'id': id})['name']

    def addChat(self, name, users):
        chat = {'name': name, 'users': users}
        inserted = self.chatCollection.insert_one(chat)
        id = str(inserted.inserted_id)
        self.chatCollection.update_one({'_id': ObjectId(id)}, {'$set': {'id': id}})

    def listOfUserChat(self, userid):
        chats = []
        for chat in self.chatCollection.find({'users': {'$in': [userid]}}):
            chats.append(chat)
            print(chat['id'])
        return chats

    def getChatById(self, chatid):
        return self.chatCollection.find_one({'id': chatid})

    def listOfMessages(self, chatid):
        m = []
        for message in self.messagesCollection.find({'chatid': chatid}):
            m.append(message)
        return m

    def addMessage(self, text, chatid, sender, time):
        message = {'text': text, 'chatid': chatid, 'sender': sender, 'time': time, 'readers': []}
        print("add message to db " + str(message))
        inserted = self.messagesCollection.insert_one(message)
        id = str(inserted.inserted_id)
        self.messagesCollection.update_one({'_id': ObjectId(id)}, {'$set': {'id': id}})
