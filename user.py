from dataclasses import dataclass

from flask import url_for
from flask_login import UserMixin
from dataBase import DataBase


@dataclass
class User(UserMixin):
    db = DataBase()

    def __init__(self):
        self.__user = None

    def fromDB(self, user_id):
        # print("request to DB")
        # print(user_id)
        if user_id == "":
            return False
        self.__user = self.db.get_user(user_id)
        print(f'[user] load user from database id:{user_id}')
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return self.__user[0]

    def get_name(self):
        return self.__user[3]

    def get_email(self):
        return self.__user[1]

    def get_age(self):
        return self.__user[6]

    def get_about(self):
        return self.__user[5]

    def get_avatar(self, app):
        img = None
        if not self.__user[7]:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: " + str(e))
        else:
            img = self.__user[7]

        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG":
            return True
        return False