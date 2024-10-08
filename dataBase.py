import sqlite3
import pymongo
from bson import ObjectId


class DataBase:
    # db_client = pymongo.MongoClient("mongodb://localhost:27017/")

    # connection = sqlite3.connect('site_database.db')
    # cursor = connection.cursor()

    def __init__(self):
        self.connection = sqlite3.connect('site_database.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.initialize_tables()
        # self.dataBase = self.db_client[dbName]
        # self.userCollection = self.dataBase["users"]
        # self.chatCollection = self.dataBase["chats"]
        # self.messagesCollection = self.dataBase["messages"]

    def initialize_tables(self):
        # Create tables if they don't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                about TEXT,
                age INT,
                avatar BLOB,
                background BLOB)
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chatname VARCHAR(255) NOT NULL,
                users TEXT)
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chatid INT NOT NULL,
                sender VARCHAR(255) NOT NULL,
                text TEXT NOT NULL)
        ''')

        self.connection.commit()

    def close_connection(self):
        self.connection.close()

    # def __del__(self):
    #    self.connection.close()

    def add_user(self, email, password, name, surname):
        try:
            self.cursor.execute('''
                INSERT INTO users (email, password, name, surname) 
                VALUES (?, ?, ?, ?)
            ''', (email, password, name, surname))
            self.connection.commit()
            print(print(f'[dataBase] add user: {email}'))

        except sqlite3.Error as e:
            print(f'[dataBase] error: {e}')
        # inserted = self.userCollection.insert_one(user)
        # self.userCollection.update_one({'email': user['email']}, {'$set': {'id': str(inserted.inserted_id),
        #                                                                  'age': "", 'aboutUser': "", 'photo': ""}})

    def check_user(self, email):
        try:
            self.cursor.execute('''
                SELECT id FROM users WHERE email = ?
            ''', (email,))
            user = self.cursor.fetchone()
            print(user)
            if user is None:
                print(f'[dataBase] check user by email email:{email} result: True')
                return True
            else:
                print(f'[dataBase] check user by email email:{email} result: False')
                return False
        except sqlite3.Error as e:
            print(f'[dataBase] error: {e}')
            return False

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = self.cursor.fetchone()
        if user_id is None:
            print(f'[dataBase] get user by id:{user_id} result: User not found')
            return False
        print(f'[dataBase] get user by id:{user_id} result: User found')
        return user

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.cursor.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.connection.commit()
        except sqlite3.Error as e:
            print("[dataBase] error: " + str(e))
            return False
        return True

    def get_user_by_email(self, email):
        self.cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = self.cursor.fetchone()
        if user:
            print(f'[dataBase] get user by email:{email} result: User found')
            return user
        else:
            print(f"[dataBase] Get user by email {email}: User not found")
            return None

    def update_user(self, user_id, name, age, about):
        # self.userCollection.update_one({'id': str(id)}, {'$set': {'name': name, 'age': age, 'aboutUser': aboutUser}})
        # print(id)
        # print(self.userCollection.find_one({'id': str(id)}))
        # print("profile updated in bd")

        self.cursor.execute('''
                UPDATE users
                SET name = ?, age = ?, about = ?
                WHERE id = ?
                ''', (name, age, about, user_id))
        self.connection.commit()
        print(f'[dataBase] update user\'s profile: id:{user_id}, name:{name}, age{age}, about:{about}  ')

    def get_hash(self, user_id):
        print(f'[dataBase] get hash of id:{user_id}')
        self.cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_password(self, user_id, new_password):
        self.cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        self.connection.commit()
        print(f'[DataBaseSQLite] Password updated for id: {user_id}')
        print(f'[dataBase] update password id:{user_id}')

    def get_list_of_users(self):
        self.cursor.execute('SELECT id, name FROM users')
        users_list = self.cursor.fetchall()
        print(f'[dataBase] get list of all users')
        return users_list

    def get_username_by_id(self, user_id):
        self.cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        if result:
            print(f'[dataBase] Username for id: {user_id} is {result[0]}')
            return result[0]
        else:
            print(f'[dataBase] User with id: {user_id} not found')
            return None

    def add_chat(self, chat_name, users):
        self.cursor.execute('INSERT INTO chats (chatname, users) VALUES (?, ?)',
                            (chat_name, ','.join(map(str, users))))
        chat_id = self.cursor.lastrowid
        self.connection.commit()
        print(f'[dataBase] add chat id:{chat_id} users: {users}')
        # return chat_id

    def get_user_chat_list(self, user_id):
        self.cursor.execute("SELECT * FROM chats WHERE users LIKE ?", ('%' + str(user_id) + '%',))
        chats = self.cursor.fetchall()
        print(f'[dataBase] get user\'s list of chats chat id:{user_id}, chats: {chats}')
        return chats

    def get_chat_by_id(self, chat_id):
        self.cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
        chat = self.cursor.fetchone()
        print(f'[dataBase] get chat by id:{chat_id}')
        return chat

    def get_list_of_messages(self, chat_id):
        self.cursor.execute('SELECT * FROM messages WHERE chat_id = ?', (chat_id,))
        messages = self.cursor.fetchall()
        print(f'[dataBase] get all messages of chat id:{chat_id}')
        return messages

    def add_message(self, text, chat_id, sender, timestamp):
        # message = {'text': text, 'chatid': chatid, 'sender': sender, 'time': time, 'readers': []}
        # print("add message to db " + str(message))
        # inserted = self.messagesCollection.insert_one(message)
        # id = str(inserted.inserted_id)
        # print(f'[dataBase] add message in chat id:{chatid} sender: {sender}, text: {text}')
        # self.messagesCollection.update_one({'_id': ObjectId(id)}, {'$set': {'id': id}})

        self.cursor.execute('''
            INSERT INTO messages (message, chat_id, sender, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (text, chat_id, sender, timestamp))
        # message_id = self.cursor.lastrowid
        self.connection.commit()
        print(f'[dataBase] add message in chat id:{chat_id} sender: {sender}, text: {text}')
        # return message_id
