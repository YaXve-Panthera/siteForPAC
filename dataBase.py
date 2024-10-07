import pymongo
from bson import ObjectId


class DataBase:
    uri = "mongodb+srv://clplaycom:q0AEWFo6KQICfQfE@cluster.qcj4r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
    db_client = pymongo.MongoClient(uri)

    uri = "mongodb+srv://clplaycom:q0AEWFo6KQICfQfE@cluster.qcj4r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"


    def __init__(self, dbName):
        self.dataBase = self.db_client[dbName]
        self.userCollection = self.dataBase["users"]
        self.chatCollection = self.dataBase["chats"]
        self.messagesCollection = self.dataBase["messages"]

    def add_user(self, user):
        inserted = self.userCollection.insert_one(user)
        self.userCollection.update_one({'email': user['email']}, {'$set': {'id': str(inserted.inserted_id),
                                                                           'age': "", 'aboutUser': "", 'photo': ""}})
        print(print(f'[dataBase] add user: {inserted}'))

    def check_user(self, email):
        if self.userCollection.find_one({'email': email}) is None:
            print(f'[dataBase] check user by email email:{email} result: True')
            return True
        else:
            print(f'[dataBase] check user by email email:{email} result: False')
            return False

    def get_user(self, id):
        if id is None:
            print(f'[dataBase] get user by id:{id} result: User not found')
            return False
        print(f'[dataBase] get user by id:{id} result: User found')
        return self.userCollection.find_one({'id': id})

    def get_user_by_email(self, email):
        print(f'[dataBase] get user by email:{email} result: User found')
        # print("request by email " + str(self.userCollection.find_one({'email': email})))
        return self.userCollection.find_one({'email': email})

    def update_user(self, id, name, age, aboutUser):
        self.userCollection.update_one({'id': str(id)}, {'$set': {'name': name, 'age': age, 'aboutUser': aboutUser}})
        # print(id)
        # print(self.userCollection.find_one({'id': str(id)}))
        # print("profile updated in bd")
        print(f'[dataBase] update user\'s profile: id:{id}, name:{name}, age{age}, about:{aboutUser}  ')

    def get_hash(self, id):
        print(f'[dataBase] get hash of id:{id}')
        return self.userCollection.find_one({'id': id})['password']

    def update_password(self, id, newpassword):
        self.userCollection.update_one({'id': str(id)}, {'$set': {'password': newpassword}})
        print(f'[dataBase] update password id:{id}')

    def get_list_of_users(self):
        l = []
        for user in self.userCollection.find():
            l.append((user['id'], user['name']))
        print(f'[dataBase] get list of all users')
        return l

    def get_username_by_id(self, id):
        print(f'[dataBase] get user\'s name by id:{id} result: User not found')
        return self.userCollection.find_one({'id': id})['name']

    def add_chat(self, name, users):
        chat = {'name': name, 'users': users}
        inserted = self.chatCollection.insert_one(chat)
        id = str(inserted.inserted_id)
        self.chatCollection.update_one({'_id': ObjectId(id)}, {'$set': {'id': id}})
        print(f'[dataBase] add chat id:{id} users: {users}')

    def get_user_chat_list(self, userid):
        chats = []
        for chat in self.chatCollection.find({'users': {'$in': [userid]}}):
            chats.append(chat)
            print(chat['id'])
        print(f'[dataBase] get user\'s list of chats chat id:{userid}, chats: {chats}')
        return chats

    def get_chat_by_id(self, chatid):
        print(f'[dataBase] get chat by id:{chatid}')
        return self.chatCollection.find_one({'id': chatid})

    def get_list_of_messages(self, chatid):
        m = []
        for message in self.messagesCollection.find({'chatid': chatid}):
            m.append(message)
        print(f'[dataBase] get all messages of chat id:{chatid}')
        return m

    def add_message(self, text, chatid, sender, time):
        message = {'text': text, 'chatid': chatid, 'sender': sender, 'time': time, 'readers': []}
        # print("add message to db " + str(message))
        inserted = self.messagesCollection.insert_one(message)
        id = str(inserted.inserted_id)
        print(f'[dataBase] add message in chat id:{chatid} sender: {sender}, text: {text}')
        self.messagesCollection.update_one({'_id': ObjectId(id)}, {'$set': {'id': id}})