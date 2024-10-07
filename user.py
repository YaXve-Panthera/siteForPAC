from dataclasses import dataclass
from flask_login import UserMixin
from dataBase import DataBase


@dataclass
class User(UserMixin):
    db = DataBase("siteBase")

    def fromDB(self, user_id):
        print("request to DB")
        print(user_id)
        if user_id == "":
            return False
        self.__user = self.db.get_user(user_id)
        print(f'[user] load user from database id:{user_id}')
        return self

    def create(self, user):
        user['age'] = ""
        user['aboutUser'] = ""
        self.__user = user
        return self

    def get_id(self):
        return self.__user['id']

    def get_name(self):
        return self.__user['name']

    def get_email(self):
        return self.__user['email']

    def get_age(self):
        return self.__user['age']

    def get_about(self):
        return self.__user['aboutUser']
