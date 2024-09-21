from dataclasses import dataclass, asdict

import pymongo
from bson import ObjectId
from dacite import from_dict
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
        self.__user = self.db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return self.__user['id']


